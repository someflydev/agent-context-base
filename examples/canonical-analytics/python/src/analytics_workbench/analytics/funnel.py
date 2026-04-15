from dataclasses import dataclass
from ..data.models import Session, FunnelStage
from ..filters import FilterState

@dataclass
class FunnelStages:
    stages: list[str]
    counts: list[int]
    drop_off_rates: list[float]

def aggregate_funnel_stages(sessions: list[Session], filters: FilterState, stages: list[FunnelStage] = None) -> FunnelStages:
    import pandas as pd
    
    if stages is None:
        from ..data.loader import get_dataset
        stages = get_dataset().funnel_stages
    
    filtered = []
    for s in sessions:
        if filters.environment and s.environment not in filters.environment: continue
        filtered.append(s)
        
    ordered_stages = stages # already have names
    stage_names = [s.stage_name for s in ordered_stages]
    
    if not filtered:
        return FunnelStages(stages=stage_names, counts=[0]*len(stage_names), drop_off_rates=[0.0]*len(stage_names))
        
    # Count how many sessions reached AT LEAST each stage
    # Since sessions just have `funnel_stage`, we assume stages are sequential
    # For a session with funnel_stage = X, it reached all stages up to X.
    # To keep it simple let's just create an arbitrary order
    order_map = {name: i for i, name in enumerate(stage_names)}
    
    counts = {name: 0 for name in stage_names}
    
    for s in filtered:
        final_order = order_map.get(s.funnel_stage, -1)
        for stage in stage_names:
            if final_order >= order_map[stage]:
                counts[stage] += 1
                
    stage_counts = [counts[name] for name in stage_names]
    drop_offs = []
    for i in range(len(stage_counts)):
        if i == 0 or stage_counts[i-1] == 0:
            drop_offs.append(0.0)
        else:
            drop_offs.append(1.0 - (stage_counts[i] / stage_counts[i-1]))
            
    return FunnelStages(
        stages=stage_names,
        counts=stage_counts,
        drop_off_rates=drop_offs
    )
