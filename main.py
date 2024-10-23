from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sympy import symbols, diff, simplify, sin, cos, tan, exp, log, sqrt, asin, acos, atan, sinh, cosh, tanh, pi, E
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class VectorFieldComponents(BaseModel):
    Fx: str
    Fy: str
    Fz: str

# Funciones que son aceptadas
allowed_functions = {
    'sin': sin, 'cos': cos, 'tan': tan,
    'asin': asin, 'acos': acos, 'atan': atan,
    'sinh': sinh, 'cosh': cosh, 'tanh': tanh,
    'exp': exp, 'log': log, 'sqrt': sqrt,
    'pi': pi, 'E': E
}

def compute_curl(Fx_str, Fy_str, Fz_str):
    x, y, z = symbols('x y z')
    
    local_dict = {'x': x, 'y': y, 'z': z, **allowed_functions}
    
    transformations = (standard_transformations + (implicit_multiplication_application,))
    
    try:
        Fx = parse_expr(Fx_str, local_dict=local_dict, transformations=transformations, evaluate=False)
        Fy = parse_expr(Fy_str, local_dict=local_dict, transformations=transformations, evaluate=False)
        Fz = parse_expr(Fz_str, local_dict=local_dict, transformations=transformations, evaluate=False)
        
        Curl_x = simplify(diff(Fz, y) - diff(Fy, z))
        Curl_y = simplify(diff(Fx, z) - diff(Fz, x))
        Curl_z = simplify(diff(Fy, x) - diff(Fx, y))
        
        return [Curl_x, Curl_y, Curl_z]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/compute_curl")
def compute_curl_endpoint(components: VectorFieldComponents):
    curl_result = compute_curl(components.Fx, components.Fy, components.Fz)
    
    curl_result_str = [str(component) for component in curl_result]
    
    return {"curl": curl_result_str}

