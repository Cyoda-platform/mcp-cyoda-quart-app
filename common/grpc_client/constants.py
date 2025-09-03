from common.config.config import GRPC_PROCESSOR_TAG

TAGS = [GRPC_PROCESSOR_TAG]
OWNER = "PLAY"
SPEC_VERSION = "1.0"
SOURCE = "SimpleSample"
JOIN_EVENT_TYPE = "CalculationMemberJoinEvent"
CALC_RESP_EVENT_TYPE = "EntityProcessorCalculationResponse"
CALC_REQ_EVENT_TYPE = "EntityProcessorCalculationRequest"
CRITERIA_CALC_REQ_EVENT_TYPE = "EntityCriteriaCalculationRequest"
CRITERIA_CALC_RESP_EVENT_TYPE = "EntityCriteriaCalculationResponse"
GREET_EVENT_TYPE = "CalculationMemberGreetEvent"
KEEP_ALIVE_EVENT_TYPE = "CalculationMemberKeepAliveEvent"
EVENT_ACK_TYPE = "EventAckResponse"
ERROR_EVENT_TYPE = "ErrorEvent"

