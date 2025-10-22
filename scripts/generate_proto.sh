#!/bin/bash
# Script to regenerate Python gRPC code from proto files
# This should be run whenever proto files are updated

set -e

echo "🔧 Generating Python gRPC code from proto files..."

# Navigate to proto directory
cd "$(dirname "$0")/../common/proto"

# Generate Python code from proto files
echo "📝 Generating from cloudevents.proto..."
python -m grpc_tools.protoc -I. \
    --python_out=. \
    --grpc_python_out=. \
    --pyi_out=. \
    cloudevents.proto

echo "📝 Generating from cyoda-cloud-api.proto..."
python -m grpc_tools.protoc -I. \
    --python_out=. \
    --grpc_python_out=. \
    --pyi_out=. \
    cyoda-cloud-api.proto

# Fix import statements in generated files
echo "🔧 Fixing import statements..."
sed -i 's/^import cloudevents_pb2/from . import cloudevents_pb2/' cyoda_cloud_api_pb2_grpc.py
sed -i 's/^import cloudevents_pb2/from . import cloudevents_pb2/' cyoda_cloud_api_pb2.py

echo "✅ Proto generation complete!"
echo ""
echo "Generated files:"
ls -lh *.py *.pyi | grep -v __pycache__

echo ""
echo "📚 The following RPC methods are now available:"
echo "  - startStreaming (bidirectional streaming)"
echo "  - entityModelManage (unary)"
echo "  - entityManage (unary)"
echo "  - entityManageCollection (server streaming)"
echo "  - entitySearch (unary)"
echo "  - entitySearchCollection (server streaming)"
echo ""
echo "🎯 Temporal query schemas supported in entitySearchCollection:"
echo "  - EntityStatsGetRequest → EntityStatsResponse"
echo "  - EntityStatsByStateGetRequest → EntityStatsByStateResponse"
echo "  - EntityChangesMetadataGetRequest → EntityChangesMetadataResponse"

