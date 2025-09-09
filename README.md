# FCA MCP Server
*Open-source AI-powered regulatory intelligence for financial services*

[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](https://choosealicense.com/licenses/mit/)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)

## 🎯 What This Solves

Financial services firms waste **hours every day** manually searching through fragmented FCA databases for regulatory information. Our open-source FCA MCP Server transforms this experience by providing **real-time, conversational access** to live FCA Register data through AI interfaces.

**Instead of this:** Manual searches across multiple FCA portals, copying firm reference numbers, cross-referencing databases
**You get this:** "Which firms can provide mortgage advice in Scotland?" → Instant, accurate answers with source citations

## 🚀 Key Benefits

- **70% reduction** in regulatory research time
- **Real-time data** from live FCA APIs (not static databases)
- **Open source** - inspect, modify, and extend freely
- **Conversational interface** - ask questions in plain English
- **Zero licensing costs** - available to all financial services firms

## 🎬 Demo

**See the FCA MCP Server in action:**






*Watch a 2-minute demo showing how regulatory questions that normally take hours are answered in seconds*

### Demo Scenarios:
- 🏛️ **Digital Asset Startup**: "Do I need FCA authorization for my custody solution?"
- 💼 **Investment Advisory**: "What are current suitability rules for high-net-worth clients?"  
- 📊 **Market Intelligence**: "Find all authorized wealth management firms in London"

## How It Works

Our MCP (Model Context Protocol) server acts as a bridge between AI assistants like Claude Desktop and the FCA's regulatory data. It:

1. **Continuously ingests** data from all FCA Register endpoints
2. **Processes and normalises** the information for AI consumption  
3. **Exposes conversational tools** for natural language queries
4. **Returns real-time results** with proper citations and context

**Architecture**: FastMCP server → Elasticsearch with semantic search → Azure OpenAI embeddings → Live FCA APIs

## 🛠️ Available Tools

The MCP Server provides these AI-accessible tools:

- **`search_fca_handbook`** - Search FCA Handbook rules and guidance
- **`search_policy_statements`** - Find FCA Policy Statements by content
- **`search_consultation_papers`** - Search regulatory proposals and consultations
- **`search_authorised_firms`** - Query the FCA register of authorised firms
- **`search_enforcement_notices`** - Search enforcement actions and fines
- **`get_firm_details`** - Get comprehensive firm information
- **`search_guidance_documents`** - Find FCA guidance and technical standards
- **`get_regulatory_updates`** - Get latest regulatory announcements

## 🎯 Use Cases

**For Compliance Teams:**
- "Find all firms with mortgage advice permissions in my region"
- "What enforcement actions were taken for conduct breaches this year?"
- "Show me recent policy changes affecting investment firms"

**For Legal & Risk:**
- "Search FCA Handbook for rules about operational resilience"
- "Find consultation papers on crypto asset regulations"
- "What are the current requirements for ESG reporting?"

**For Business Development:**
- "Which competitors have similar FCA permissions to us?"
- "Find recently authorised fintech firms"
- "Show me regulatory barriers for new product launches"

## 🚀 Quick Start (5 Minutes)

**Prerequisites:** Docker, Node.js, Claude Desktop, Azure OpenAI API key

1. **Clone and configure:**
   ```bash
   git clone https://github.com/trailblazelabs/fca-mcp.git
   cd fca-mcp
   cp .env.example .env
   # Edit .env with your Azure OpenAI credentials
   ```

2. **One-command setup:**
   ```bash
   make dev_setup_from_scratch
   ```

3. **Connect to Claude Desktop:**
   ```json
   {
     "mcpServers": {
       "fca-mcp": {
         "command": "npx",
         "args": ["mcp-remote", "http://localhost:8080/mcp/", "--allow-http"]
       }
     }
   }
   ```

4. **Start asking questions!**
   - "Search for wealth management firms in London"
   - "Find recent enforcement notices about market manipulation"
   - "Show me policy changes affecting crypto firms"

## 🔧 Technical Deep Dive

### Prerequisites for Local Development

- Python >= 3.12
- [uv](https://docs.astral.sh/uv/) (Python package manager)
- Docker and Docker Compose
- Node.js (for mcp-remote)

### Local Development Setup

1. **Install uv** (if not already installed):
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **Clone and set up the project**:
   ```bash
   git clone <repository>
   cd fca-mcp

   # Install dependencies with uv
   uv sync --extra dev
   ```

3. **Available Make commands**:
   ```bash
   make install           # Install all dependencies
   make test              # Run tests
   make test_integration  # Run integration tests (slow on first run)
   make lint              # Check code formatting
   make format            # Format and fix code
   make safe              # Run security checks

   # Pre-commit hooks
   make pre-commit-install  # Install pre-commit hooks
   make pre-commit         # Run pre-commit on all files

   # Docker operations
   make run             # Start services with Docker Compose
   make stop            # Stop Docker services
   make logs            # View MCP server logs

   # Development helpers
   make mcp_test        # Test MCP server connection
   make es_health       # Check Elasticsearch health
   ```

4. **Run the MCP server locally**:
   ```bash
   make run_mcp_server
   # Or directly with uv:
   uv run fca-mcp serve
   ```

### Project Structure

```
fca-mcp/
├── fca_mcp/                 # Main Python package
│   ├── cli.py               # CLI interface
│   ├── models.py            # Data models
│   ├── mcp_server/          # MCP server implementation
│   │   ├── api.py           # API endpoints and tool definitions
│   │   ├── handlers.py      # Elasticsearch query handlers
│   │   ├── main.py          # FastAPI application setup
│   │   └── utils.py         # Utility functions
│   └── ...                  # Other modules
├── tests/                   # Test suite
│   ├── mcp_server/          # MCP server tests
│   └── ...                  # Other tests
├── Dockerfile.mcp-server    # MCP server container configuration
├── docker-compose.yaml      # Service orchestration
└── README.md                # This file
```

### CLI Commands

The project includes a unified CLI for data management and server operations:

```bash
# Initialize Elasticsearch indices and inference endpoints
fca-mcp init-elasticsearch

# Run the MCP server
fca-mcp serve

# Load different types of FCA data
fca-mcp load-data handbook
fca-mcp load-data policy-documents
fca-mcp load-data consultation-papers
fca-mcp load-data firms-register
fca-mcp load-data enforcement-notices

# Delete all data
fca-mcp delete-elasticsearch
```

### Data Structure

The system works with several types of FCA regulatory documents:

**FCA Handbook** (Index: `fca_mcp_handbook`):
- Rules and guidance sections with semantic search
- Cross-references between sections
- Section hierarchy and numbering

**Policy Statements** (Index: `fca_mcp_policy_statements`):
- Final policy decisions and statements
- Semantic search on policy content
- PS number references and dates

**Consultation Papers** (Index: `fca_mcp_consultation_papers`):
- Regulatory proposals and consultations
- Comment periods and responses
- CP number references

**Authorised Firms** (Index: `fca_mcp_authorised_firms`):
- Firms and individuals register
- Permissions and restrictions
- Contact and status information

**Enforcement Notices** (Index: `fca_mcp_enforcement_notices`):
- Disciplinary actions and fines
- Decision notices and final notices
- Firm and individual sanctions

**Data Loading Process**:
1. **Fetch** from FCA APIs and web sources
2. **Transform** into structured models with computed fields
3. **Embed** using Azure OpenAI for semantic search
4. **Index** into Elasticsearch with proper mappings

### Daily Data Ingestion

To keep the FCA data up-to-date, a daily ingestion mechanism is provided:

```bash
make ingest_daily
```

This runs the equivalent of:
```bash
fca-mcp load-data handbook --incremental
fca-mcp load-data policy-documents --recent
fca-mcp load-data enforcement-notices --recent
```

## Usage Examples

Once connected to Claude, you can use natural language queries like:

**FCA Handbook:**
- "Search the FCA Handbook for rules about mortgage lending"
- "Find guidance on consumer credit regulations"
- "Show me the latest updates to conduct of business rules"

**Policy and Consultation:**
- "Find policy statements about ESG and sustainability"
- "Search consultation papers on crypto asset regulations"
- "Show me recent policy changes affecting investment firms"

**Firm Information:**
- "Search for authorised wealth management firms in London"
- "Find details about a specific firm's permissions"
- "Show me recent authorisation decisions"

**Enforcement:**
- "Search enforcement notices about market manipulation"
- "Find recent fines for conduct breaches"
- "Show me disciplinary actions against individuals"

**Regulatory Research:**
- "Find all FCA guidance on operational resilience"
- "Search for rules affecting fintech companies"
- "Show me consumer protection requirements for investments"

### Logs and Debugging

**View server logs**:
```bash
docker-compose logs mcp-server
```

**Enable debug mode** in Claude config by adding `--debug` flag.

**Check Elasticsearch status**:
```bash
curl http://localhost:9200/_cat/health?v
# Or use the make command:
make es_health
```

## Troubleshooting

### Common Issues

**MCP Connection Issues**
- Ensure MCP server is running on port 8080
- The MCP server runs on `/{MCP_ROOT_PATH}/mcp`, not `/MCP_ROOT_PATH`
- Verify Claude Desktop configuration is correct

**Data Loading Failures**
- Check Azure OpenAI credentials in `.env` file
- Ensure Elasticsearch is running and accessible
- Verify network connectivity to FCA APIs and websites
- Use `--ll DEBUG` flag for detailed logging

**Elasticsearch issues**
- Verify inference endpoints are created: `fca-mcp init-elasticsearch`
- Use https://elasticvue.com/ to inspect the Elasticsearch instance

## Optional: Parliamentary horizon scanning (Enterprise)

Forward‑looking risk monitoring to anticipate regulatory change:

- HM Treasury and Select Committee hearings (Hansard)
- Financial Services Acts and Statutory Instruments affecting FCA perimeter
- Treasury consultations and policy statements

This module is available in the Enterprise edition and integrates with the same MCP interface for proactive alerts and research.

## Contact

**Interested in enterprise access or collaboration?**

📅 **Schedule a call**: [https://cal.com/trailblazelabs](https://cal.com/trailblazelabs)

## License

MIT License - see LICENSE file for details
