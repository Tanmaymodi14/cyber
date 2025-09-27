# 🤖 AI Policy Analysis - Command Line Interface

A simple, powerful command-line tool for analyzing non-technical policy documents against FedRAMP controls.

## Quick Start

```bash
cd /Users/tanmaymodi/cyber/proTecht
./policy your_policy.txt
```

## Usage Examples

### Basic Analysis
```bash
# Analyze a policy document
./policy access_control_policy.txt

# With custom name
./policy my_policy.txt --name "Corporate Access Control Policy"
```

### Detailed Analysis
```bash
# Show verbose output with citations and detailed recommendations
./policy incident_response_policy.txt --verbose
```

### JSON Output (for scripts/automation)
```bash
# Get JSON output for programmatic use
./policy security_policy.txt --json

# Extract just the compliance score
./policy security_policy.txt --json | jq '.summary.compliance_pct'

# Get failed controls
./policy security_policy.txt --json | jq '.controls[] | select(.status == "fail") | .control_id'
```

### Batch Processing
```bash
# Analyze multiple policies
for policy in *.txt; do
  echo "=== $policy ==="
  ./policy "$policy" --json | jq '.summary'
done

# Generate compliance report for all policies
echo "Policy,Compliance%" > compliance_report.csv
for policy in *.txt; do
  score=$(./policy "$policy" --json | jq -r '.summary.compliance_pct')
  echo "$policy,$score" >> compliance_report.csv
done
```

## Output Formats

### Human-Readable (Default)
- Clean, formatted output with emojis
- Compliance summary with scores
- Control-by-control analysis
- Missing elements and recommendations

### Verbose Mode (`--verbose`)
- All default information plus:
- Detailed analysis reasoning
- Policy citations (quotes from your document)
- Template references

### JSON Mode (`--json`)
- Structured output for automation
- All data fields included
- Perfect for integration with other tools

## Requirements

- Policy documents must be in `.txt` format
- OpenAI API key should be set for best results (falls back to heuristic analysis)
- Virtual environment should be activated (handled automatically by the `./policy` script)

## Return Codes

- `0`: Success
- `1`: File not found, wrong format, or analysis error

## Integration Examples

### With jq (JSON processing)
```bash
# Get controls that need attention
./policy my_policy.txt --json | jq '.controls[] | select(.status != "pass")'

# Summary statistics
./policy my_policy.txt --json | jq '{
  policy: .policy_name,
  score: .summary.compliance_pct,
  needs_work: .summary.failed + .summary.partial
}'
```

### With curl (if using the web API instead)
```bash
curl -X POST http://localhost:5001/analyze_policy \
  -F "file=@my_policy.txt" \
  -F "policy_name=My Policy" | jq '.summary'
```

### Python Integration
```python
import subprocess
import json

# Run analysis and get results
result = subprocess.run(['./policy', 'my_policy.txt', '--json'], 
                       capture_output=True, text=True)
data = json.loads(result.stdout)
print(f"Compliance: {data['summary']['compliance_pct']}%")
```

## Control Analysis

The tool analyzes against these FedRAMP non-technical controls:
- **AC-1**: Access Control Policy and Procedures
- **AC-5**: Separation of Duties  
- **AC-6**: Least Privilege
- **IR-2**: Incident Response Training
- **IR-6**: Incident Reporting
- **PL-2**: System Security Plan
- **PM-10**: Security Authorization Process
- **PM-11**: Mission/Business Process Definition
- **SR-1**: Supply Chain Risk Management Policy

## Advanced Features

### AI-Powered Analysis
When OpenAI API key is available:
- Intelligent document section splitting
- LLM-powered control mapping
- Template-grounded validation
- Rich citations and recommendations

### Fallback Analysis  
When AI is unavailable:
- Heuristic keyword analysis
- Pattern-based control mapping
- Basic compliance checking

### Confidence Scoring
Every result includes confidence metrics to help you understand the reliability of the analysis.
