
decisions = []

for decision in whatever_has_the_decisions_you_want_to_upload:
    decisions.append(
        DecisionWithFeatureIds(
            feature_id=["whatever you are using for feature ids"],
            decision=MDLDecision(
                fetch_validate_decision=FetchValidateDecision(...)
            ),
        )
    )

with grpc.insecure_channel(METASERVICE_AUTHORITY) as c:
    stub = metaservice_pb2.MetadataServiceStub(c)

    stub.AddDecision(
        AddDecisionRequest(
            activity_start_time=...,
            agent_id=...,
            used=[...],
            decision_with_feature_ids=decisions
        )
    )
