import logging
from typing import Any

from mcp.server.fastmcp.server import FastMCP
from pydantic import Field

logger = logging.getLogger(__name__)

# Community Edition MCP server (interfaces only; no implementation)
mcp_server = FastMCP(name="FCA MCP Server (Community Edition)", stateless_http=True)


def _enterprise_only(tool_name: str, **params: Any) -> dict[str, Any]:
    logger.info("Community edition tool called: %s", tool_name)
    return {
        "tool": tool_name,
        "status": 501,
        "error": "Enterprise-only endpoint. Schedule access at https://cal.com/trailblazelabs",
        "params": {k: v for k, v in params.items() if v is not None},
    }


@mcp_server.tool("search_fca_handbook")
async def search_fca_handbook(
    query: str = Field(..., description="Search text to find in FCA Handbook rules and guidance"),
    chapter: str | None = Field(None, description="Specific handbook chapter (e.g., 'PRIN', 'COBS', 'SYSC')"),
    content_type: str | None = Field(None, description="Filter by content type: 'rule', 'guidance', 'schedule'"),
    is_current: bool = Field(True, description="Whether to search only current rules (default True)"),
    limit: int = Field(10, description="Maximum number of results to return (max 50)"),
) -> Any:
    return _enterprise_only("search_fca_handbook", query=query, chapter=chapter, content_type=content_type, is_current=is_current, limit=limit)


@mcp_server.tool("search_policy_statements")
async def search_policy_statements(
    query: str = Field(..., description="Search text to find in FCA Policy Statements"),
    policy_area: str | None = Field(None, description="Filter by policy area"),
    from_date: str | None = Field(None, description="Start date (YYYY-MM-DD)"),
    to_date: str | None = Field(None, description="End date (YYYY-MM-DD)"),
    ps_number: str | None = Field(None, description="Specific PS number (e.g., 'PS24/1')"),
    limit: int = Field(10, description="Maximum number of results to return (max 50)"),
) -> Any:
    return _enterprise_only("search_policy_statements", query=query, policy_area=policy_area, from_date=from_date, to_date=to_date, ps_number=ps_number, limit=limit)


@mcp_server.tool("search_consultation_papers")
async def search_consultation_papers(
    query: str = Field(..., description="Search text to find in FCA Consultation Papers"),
    policy_area: str | None = Field(None, description="Filter by policy area"),
    from_date: str | None = Field(None, description="Start date (YYYY-MM-DD)"),
    to_date: str | None = Field(None, description="End date (YYYY-MM-DD)"),
    cp_number: str | None = Field(None, description="Specific CP number (e.g., 'CP24/1')"),
    open_for_consultation: bool | None = Field(None, description="Filter by open consultations"),
    limit: int = Field(10, description="Maximum number of results to return (max 50)"),
) -> Any:
    return _enterprise_only("search_consultation_papers", query=query, policy_area=policy_area, from_date=from_date, to_date=to_date, cp_number=cp_number, open_for_consultation=open_for_consultation, limit=limit)


@mcp_server.tool("search_authorised_firms")
async def search_authorised_firms(
    query: str | None = Field(None, description="Search text to find in firm names or details"),
    firm_name: str | None = Field(None, description="Specific firm name to search for"),
    city: str | None = Field(None, description="Filter by city/location"),
    permissions: str | None = Field(None, description="Filter by permissions"),
    firm_status: str = Field("Authorised", description="Firm status filter (default: 'Authorised')"),
    limit: int = Field(10, description="Maximum number of results to return (max 50)"),
) -> Any:
    return _enterprise_only("search_authorised_firms", query=query, firm_name=firm_name, city=city, permissions=permissions, firm_status=firm_status, limit=limit)

