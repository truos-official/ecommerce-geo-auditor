"""Stage 4: AI Agent Prompting orchestrator."""

from core.context import AuditContext, AgentResult
from agents.client import AgentClient, ModelConfig
from stages.prompts import generate_reference_facts, build_unbranded_prompts
from stages.scoring import score_response
from stages.retrieval_analysis import analyze_retrieval
from stages.traffic_analysis import analyze_traffic


async def run_stage4(context: AuditContext, config: dict) -> AuditContext:
    """Stage 4: Test AI agents with dual-mode."""

    # Generate reference facts
    if context.product_schema:
        context.reference_facts = generate_reference_facts(
            context.product_schema.__dict__,
            context.content_blocks,
            context.product_category
        )
    else:
        # Fallback: minimal reference facts from content blocks
        context.reference_facts = {
            "core": {
                "product_id": None,
                "product_name": "Unknown Product",
                "canonical_url": context.url
            }
        }

    # Build unbranded prompts
    context.prompts = build_unbranded_prompts(
        context.reference_facts,
        context.siblings,
        context.product_category,
        config.get("prompts", {}).get("pass_threshold", 70)
    )

    # Initialize agent client
    client = AgentClient()

    # Get enabled agents
    agents_config = config.get("agents", {})
    testing_scope = config.get("testing_scope", "flagship_only")

    results = []

    # Test each agent
    for agent_name, agent_config in agents_config.items():
        if not agent_config.get("enabled", True):
            continue

        test_training = agent_config.get("test_training_mode", True)
        models = agent_config.get("models", [])

        # Filter by tier
        if testing_scope == "flagship_only":
            models = [m for m in models if m.get("tier") == "flagship"]

        # Test each model
        for model_dict in models[:1]:  # Limit to 1 model per agent for now
            model = ModelConfig(
                name=model_dict["name"],
                provider=agent_name,
                tier=model_dict.get("tier", "flagship")
            )

            # Test each prompt (limit to first 2 for demo)
            for prompt_exec in context.prompts[:2]:
                # Training mode
                training_response = None
                training_score = 0.0

                if test_training and agent_name != "perplexity":
                    training_response = await client.call_agent(
                        agent_name, model, prompt_exec.prompt, "training"
                    )
                    training_score = score_response(
                        training_response.text,
                        context.reference_facts
                    )

                # Live mode
                live_response = await client.call_agent(
                    agent_name, model, prompt_exec.prompt, "live"
                )
                live_score = score_response(
                    live_response.text,
                    context.reference_facts
                )

                # Analyze retrieval
                retrieval_analysis = analyze_retrieval(
                    live_response,
                    context.url,
                    context.reference_facts
                )

                # Analyze traffic
                from urllib.parse import urlparse
                target_domain = urlparse(context.url).netloc
                traffic_analysis = analyze_traffic(
                    live_response,
                    context.url,
                    target_domain
                )

                # Create result
                result = AgentResult(
                    agent_name=agent_name,
                    model_name=model.name,
                    prompt_id=prompt_exec.id,
                    dimension=prompt_exec.dimension,
                    training_response=training_response.text if training_response else "",
                    training_score=training_score,
                    training_hallucinations=[],
                    training_evidence_id="",
                    live_response=live_response.text,
                    live_score=live_score,
                    live_hallucinations=[],
                    live_evidence_id="",
                    retrieval_analysis=retrieval_analysis,
                    traffic_analysis=traffic_analysis,
                    improvement_from_live=live_score - training_score
                )

                results.append(result)

    context.agent_results = results

    return context
