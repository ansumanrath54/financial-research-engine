from pydantic import BaseModel, Field

class UsageTelemetry(BaseModel):
    input_tokens: int = Field(default=0, ge=0)
    output_tokens: int = Field(default=0, ge=0)
    estimated_cost_usd: float = Field(default=0.0, ge=0.0)
    api_calls: int = Field(default=0, ge=0)

    def accumulate(self, in_tokens: int, out_tokens: int, in_cost_per_m: float = 3.0, out_cost_per_m: float = 15.0) -> None:
        self.input_tokens += in_tokens
        self.output_tokens += out_tokens
        self.api_calls += 1
        cost = (self.input_tokens * (in_cost_per_m / 1_000_000)) + (self.output_tokens * (out_cost_per_m / 1_000_000))
        self.estimated_cost_usd = round(cost, 5)