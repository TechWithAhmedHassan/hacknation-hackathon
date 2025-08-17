from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, field_validator

VALID_AA = set("ACDEFGHIKLMNPQRSTVWY")  # 20 standard amino acids

app = FastAPI()

# Mount static files directory for css/js/images
app.mount("/static", StaticFiles(directory="app/static"), name="static")

templates = Jinja2Templates(directory="app/templates")


class SequenceInput(BaseModel):
    sequence: str

    @field_validator("sequence")
    def validate_sequence(cls, v):
        seq = v.strip().upper()
        if not seq:
            raise ValueError("Sequence cannot be empty")
        if any(aa not in VALID_AA for aa in seq):
            invalid = sorted(set(aa for aa in seq if aa not in VALID_AA))
            raise ValueError(f"Invalid amino acid(s): {', '.join(invalid)}")
        return seq


def classify_protein_family(sequence: str) -> str:
    """
    Placeholder for protein family classification.
    Replace this logic with a real classifier or ML model.
    Example rule-based classification:
      - If sequence contains 'C' frequently, classify as 'Disulfide-rich family'
      - If sequence has many 'K' or 'R', classify as 'Basic protein family'
      - Otherwise, classify as 'General protein family'
    """
    seq = sequence.upper()
    c_count = seq.count('C')
    k_count = seq.count('K')
    r_count = seq.count('R')
    if c_count / len(seq) > 0.1:
        return "Disulfide-rich family"
    elif (k_count + r_count) / len(seq) > 0.15:
        return "Basic protein family"
    else:
        return "General protein family"


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "error": None})


@app.post("/predict", response_class=HTMLResponse)
async def predict(request: Request, sequence: str = Form(...)):
    try:
        validated_input = SequenceInput(sequence=sequence)
    except Exception as e:
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "error": str(e),
            },
        )

    family = classify_protein_family(validated_input.sequence)

    return templates.TemplateResponse(
        "result.html",
        {
            "request": request,
            "sequence": validated_input.sequence,
            "family": family,
        },
    )