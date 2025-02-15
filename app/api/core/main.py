from fastapi import FastAPI, HTTPException, Response, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, BaseSettings
from typing import Dict, List, Optional, Union
import io
import traceback
import pandas as pd
import json
import tempfile
import os
import uvicorn
from edbo.plus.optimizer import EDBOplus
from edbo.plus.scope_generator import create_reaction_scope
from sklearn.preprocessing import MinMaxScaler, StandardScaler
app = FastAPI()

class Settings(BaseSettings):
    temp_dir: str = "/data/tmp"
    max_file_size: int = 1024*1024*10  # 10MB

settings = Settings()

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:5173").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ScopeGenerateRequest(BaseModel):
    components: Dict[str, List[Union[str, float]]]
    filename: str

class OptimizationRequest(BaseModel):
    objectives: List[str]
    objective_mode: List[str]
    objective_thresholds: List[Optional[float]]
    batch: int
    init_sampling_method: str
    seed: int
    get_predictions: bool
    acquisition_function: str
    sigma_uncertainty: float
    continuous_features: bool
    add_random_samples: bool

@app.post("/api/v1/scope/generate")
async def generate_scope(request: ScopeGenerateRequest):
    try:
        print("接收到的请求数据:", request.dict())
        
        with tempfile.TemporaryDirectory(dir=settings.temp_dir) as temp_dir:
            try:
                df = create_reaction_scope(
                    components=request.components,
                    directory=temp_dir,
                    filename="temp.csv",
                    check_overwrite=False
                )
                
                csv_content = df.to_csv(index=False)
                
                return Response(
                    content=csv_content,
                    media_type="text/csv",
                    headers={
                        "Content-Disposition": f'attachment; filename="{request.filename}"'
                    }
                )
            except Exception as e:
                print("生成实验范围时出错:", str(e))
                print("错误堆栈:", traceback.format_exc())
                raise HTTPException(
                    status_code=500,
                    detail=f"生成实验范围失败: {str(e)}\n{traceback.format_exc()}"
                )
    except Exception as e:
        print("请求处理时出错:", str(e))
        print("错误堆栈:", traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=f"请求处理失败: {str(e)}\n{traceback.format_exc()}"
        )

@app.post("/api/v1/data/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        # 保存文件到临时目录（使用配置的临时目录）
        with tempfile.TemporaryDirectory(dir=settings.temp_dir) as temp_dir:
            content = await file.read()
            # 检查文件大小
            if len(content) > settings.max_file_size:
                raise HTTPException(
                    status_code=413,
                    detail=f"文件大小超过限制 {settings.max_file_size/1024/1024}MB"
                )
            file_path = os.path.join(temp_dir, file.filename)
            with open(file_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)
            
            return {"filename": file.filename}
            
    except Exception as e:
        print("文件上传失败:", str(e))
        print("错误堆栈:", traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=f"文件上传失败: {str(e)}"
        )

@app.post("/api/v1/optimization/run")
async def run_optimization(
    file: UploadFile = File(...),
    objectives: str = Form(...),
    objective_mode: str = Form(...),
    objective_thresholds: str = Form(...),
    batch: int = Form(...),
    init_sampling_method: str = Form(...),
    seed: int = Form(...),
    get_predictions: bool = Form(...),
    acquisition_function: str = Form(...),
    sigma_uncertainty: float = Form(...),
    continuous_features: bool = Form(...),
    add_random_samples: bool = Form(...),
):
    response_headers = {
        "Access-Control-Expose-Headers": "Content-Disposition",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type"
    }
    try:
        content = await file.read()
        csv_file = io.StringIO(content.decode())
        df = pd.read_csv(csv_file)
        
        objectives_list = json.loads(objectives)
        objective_mode_list = json.loads(objective_mode)
        objective_thresholds_list = json.loads(objective_thresholds)
        
        print("优化参数:")
        print(f"目标: {objectives_list}")
        print(f"模式: {objective_mode_list}")
        print(f"阈值: {objective_thresholds_list}")
        
        for column in df.columns:
            try:
                df[column] = pd.to_numeric(df[column], errors='ignore')
            except:
                continue
        
        print("数据类型:")
        print(df.dtypes)
        
        edbo = EDBOplus()
        obj_in_df = [obj for obj in objectives_list if obj in df.columns]
        
        if len(obj_in_df) == 0:
            print("目标列不存在，进入初始实验设计阶段")
            df = edbo._init_sampling(df=df, batch=batch, seed=seed, sampling_method=init_sampling_method)
            for objective in objectives_list:
                if objective not in df.columns:
                    df[objective] = ['PENDING'] * len(df)
            return Response(
                content=df.to_csv(index=False),
                media_type="text/csv",
                headers={"Content-Disposition": f'attachment; filename="initial_design.csv"'}
            )
                
        completed_experiments = df[~df[objectives_list[0]].isna()]
        if len(completed_experiments) < 3:
            raise HTTPException(
                status_code=400,
                detail="需要至少3个完成的实验数据才能进行优化"
                )
              
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_file = os.path.join(temp_dir, "optimization_data.csv")
            df.to_csv(temp_file, index=False)
        

            try:
                result_df = edbo.run(
                    objectives=objectives_list,
                    objective_mode=objective_mode_list,
                    objective_thresholds=objective_thresholds_list,
                    batch=batch,
                    init_sampling_method=init_sampling_method,
                    seed=seed,
                    get_predictions=get_predictions,
                    acquisition_function=acquisition_function,
                    sigma_uncertainty=sigma_uncertainty,
                    continuous_features=continuous_features,
                    add_random_samples=add_random_samples,
                    filename="optimization_data.csv",
                    directory=temp_dir
                )

                if isinstance(result_df, pd.DataFrame) and 'priority' in result_df.columns:
                    df['priority'] = result_df['priority'].values
                
                csv_content = result_df.to_csv(index=False)
                response = Response(
                    content=csv_content,
                    media_type="text/csv",
                    headers={
                        "Content-Disposition": f'attachment; filename="optimization_results.csv"',
                        "Content-Type": "text/csv",
                        "Content-Length": str(len(csv_content))
                    }
                )
                return response
                
            except Exception as e:
                print("优化过程出错:", str(e))
                print("错误堆栈:", traceback.format_exc())
                raise HTTPException(
                    status_code=500,
                    detail=f"优化失败: {str(e)}"
                )
                
    except HTTPException:
        raise
    except Exception as e:
        print("请求处理出错:", str(e))
        print("错误堆栈:", traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=f"请求处理失败: {str(e)}"
        )

@app.get("/api/v1/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,  # 生产环境关闭热重载
        workers=int(os.getenv("UVICORN_WORKERS", 1))
    )
