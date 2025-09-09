import hashlib
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, computed_field, field_serializer, field_validator


class DebateParent(BaseModel):
    """Model for debate parent hierarchy information."""

    model_config = ConfigDict(extra="ignore")

    Id: int
    Title: str
    ParentId: int | None
    ExternalId: str


class ElasticDocument(BaseModel):
    """Base class for Elasticsearch documents with document URI."""

    created_at: datetime = Field(default_factory=datetime.now)

    @computed_field
    @property
    def document_uri(self) -> str:
        message = "Subclasses must implement this method"
        raise NotImplementedError(message)


class Contribution(ElasticDocument):
    """Model for Hansard contributions/speeches in Parliament."""

    model_config = ConfigDict(extra="forbid")

    MemberName: str | None = None
    MemberId: int | None = None
    AttributedTo: str | None = None
    ItemId: int | None = None
    ContributionExtId: str | None = None
    ContributionText: str | None = None
    ContributionTextFull: str | None = None
    HRSTag: str | None = None
    HansardSection: str | None = None
    DebateSection: str | None = None
    DebateSectionId: int | None = None
    DebateSectionExtId: str | None = None
    SittingDate: datetime | None = None
    Section: str | None = None
    House: str | None = None
    OrderInDebateSection: int | None = None
    DebateSectionOrder: int | None = None
    Rank: int | None = None
    Timecode: datetime | None = None
    debate_parents: list[DebateParent] | None = None

    @computed_field
    @property
    def debate_url(self) -> str:
        return f"https://hansard.parliament.uk/{self.House}/{self.SittingDate:%Y-%m-%d}/debates/{self.DebateSectionExtId}/link"

    @computed_field
    @property
    def contribution_url(self) -> str:
        if self.ContributionExtId is None:
            return None
        return f"{self.debate_url}#contribution-{self.ContributionExtId}"

    @computed_field
    @property
    def document_uri(self) -> str:
        if self.ContributionExtId is None:
            # if external id is None, then use a hash of the text and order in section
            doc_hash = hashlib.sha256(
                f"{self.DebateSectionExtId}_{self.ContributionText}_{self.OrderInDebateSection}".encode()
            ).hexdigest()
            return f"debate_{self.DebateSectionExtId}_contrib_{doc_hash}"
        else:
            return f"debate_{self.DebateSectionExtId}_contrib_{self.ContributionExtId}"

    def __str__(self):
        """String representation of contribution."""
        res = f"\nContribution {self.OrderInDebateSection}"
        res += f"\nSpeaker: {self.AttributedTo}"
        res += f"\n{self.ContributionText}\n"

        return res


class ContributionsResponse(BaseModel):
    """API response model for contributions list."""

    Results: list[Contribution]
    TotalResultCount: int

    model_config = ConfigDict(extra="ignore")


# Parliamentary Questions


class Member(BaseModel):
    """
    Represents a parliamentary member with their associated details.

    Attributes:
        id: Unique identifier for the member
        listAs: The member's listing name
        name: Full name of the member
        party: Political party affiliation
        partyColour: Colour associated with the party
        partyAbbreviation: Short form of the party name
        memberFrom: Constituency or area represented
        thumbnailUrl: URL to member's thumbnail image
    """

    id: int
    listAs: str | None = None
    name: str | None = None
    party: str | None = None
    partyColour: str | None = None
    partyAbbreviation: str | None = None
    memberFrom: str | None = None
    thumbnailUrl: str | None = None


class Attachment(BaseModel):
    """
    Represents an attachment associated with a parliamentary question.

    Attributes:
        url: Location of the attachment
        title: Name or description of the attachment
        fileType: Format of the attachment
        fileSizeBytes: Size of the attachment in bytes
    """

    url: str | None = None
    title: str | None = None
    fileType: str | None = None
    fileSizeBytes: int | None = None


class GroupedQuestionDate(BaseModel):
    """
    Represents a grouped question with its date information.

    Attributes:
        questionUin: Unique identifier for the question
        dateTabled: When the question was submitted
    """

    questionUin: str | None = None
    dateTabled: datetime

    @field_validator("dateTabled", mode="before")
    @classmethod
    def parse_datetime(cls, value) -> datetime:
        """Convert ISO format datetime string to datetime object."""
        if isinstance(value, str):
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        return value


class ParliamentaryQuestion(ElasticDocument):
    """
    Represents a parliamentary question with its associated metadata and answer.

    This model includes information about the asking member, answering member,
    question content, answer content, and various timestamps and status flags.
    """

    id: int
    askingMemberId: int
    askingMember: Member | None = None
    house: str
    memberHasInterest: bool
    dateTabled: datetime
    dateForAnswer: datetime | None = None
    uin: str | None = None
    questionText: str | None = None
    answeringBodyId: int
    answeringBodyName: str | None = None
    isWithdrawn: bool
    isNamedDay: bool
    groupedQuestions: list[str] = []
    answerIsHolding: bool | None = None
    answerIsCorrection: bool | None = None
    answeringMemberId: int | None = None
    answeringMember: Member | None = None
    correctingMemberId: int | None = None
    correctingMember: Member | None = None
    dateAnswered: datetime | None = None
    answerText: str | None = None
    originalAnswerText: str | None = None
    comparableAnswerText: str | None = None
    dateAnswerCorrected: datetime | None = None
    dateHoldingAnswer: datetime | None = None
    attachmentCount: int
    heading: str | None = None
    attachments: list[Attachment] = []
    groupedQuestionsDates: list[GroupedQuestionDate] = []
    created_at: datetime = Field(default_factory=datetime.now)

    @field_serializer(
        "dateTabled",
        "dateForAnswer",
        "dateAnswered",
        "dateAnswerCorrected",
        "dateHoldingAnswer",
    )
    def serialize_datetime(self, dt: datetime | None) -> str | None:
        """Serialize datetime fields to ISO format strings."""
        return dt.isoformat() if dt else None

    @computed_field
    @property
    def document_uri(self) -> str:
        return f"pq_{self.id}"

    @property
    def is_truncated(self) -> bool:
        """Check if question/answer text is truncated."""
        return (self.questionText is not None and self.questionText.endswith("...")) or (
            self.answerText is not None and self.answerText.endswith("...")
        )

    model_config = {"extra": "ignore"}


class Link(BaseModel):
    """
    Represents an API link with its properties.

    Attributes:
        rel: Relationship type of the link
        href: URL of the link
        method: HTTP method to be used
    """

    rel: str
    href: str
    method: str


class PQResultItem(BaseModel):
    """
    Represents the API response for a question query.

    Attributes:
        value: The parliamentary question data
        links: Related API links
    """

    value: ParliamentaryQuestion
    links: list[Link]


class ParliamentaryQuestionsResponse(BaseModel):
    results: list[PQResultItem]
    totalResults: int

    model_config = ConfigDict(extra="ignore")

    @property
    def questions(self) -> list[ParliamentaryQuestion]:
        """Extract questions from results."""
        return [item.value for item in self.results]


# =============================================================================
# FCA-Specific Data Models
# =============================================================================

class FCAHandbookSection(ElasticDocument):
    """Model for FCA Handbook sections and rules."""
    
    model_config = ConfigDict(extra="forbid")
    
    section_id: str
    chapter: str | None = None
    section_number: str | None = None
    title: str
    content: str
    content_type: str | None = None  # "rule", "guidance", "schedule", etc.
    effective_date: datetime | None = None
    last_updated: datetime | None = None
    is_current: bool = True
    superseded_by: str | None = None
    related_sections: list[str] = []
    source_url: str | None = None
    
    @computed_field
    @property
    def handbook_url(self) -> str:
        """Generate URL to the FCA Handbook section."""
        if self.section_id:
            return f"https://www.handbook.fca.org.uk/handbook/{self.section_id}"
        return None
    
    @computed_field
    @property
    def document_uri(self) -> str:
        return f"handbook_{self.section_id}"


class FCAPolicyStatement(ElasticDocument):
    """Model for FCA Policy Statements."""
    
    model_config = ConfigDict(extra="forbid")
    
    ps_number: str  # e.g., "PS24/1"
    title: str
    publication_date: datetime
    effective_date: datetime | None = None
    summary: str | None = None
    content: str
    policy_area: str | None = None
    consultation_paper: str | None = None  # Related CP reference
    contact_details: str | None = None
    attachments: list[str] = []
    source_url: str | None = None
    
    @computed_field
    @property
    def fca_url(self) -> str:
        """Generate URL to the FCA Policy Statement."""
        return f"https://www.fca.org.uk/publications/policy-statements/{self.ps_number.lower().replace('/', '-')}"
    
    @computed_field
    @property
    def document_uri(self) -> str:
        return f"policy_statement_{self.ps_number.replace('/', '_')}"


class FCAConsultationPaper(ElasticDocument):
    """Model for FCA Consultation Papers."""
    
    model_config = ConfigDict(extra="forbid")
    
    cp_number: str  # e.g., "CP24/1"
    title: str
    publication_date: datetime
    consultation_closes: datetime | None = None
    summary: str | None = None
    content: str
    policy_area: str | None = None
    cost_benefit_analysis: bool = False
    compatibility_statement: bool = False
    contact_details: str | None = None
    attachments: list[str] = []
    source_url: str | None = None
    
    @computed_field
    @property
    def fca_url(self) -> str:
        """Generate URL to the FCA Consultation Paper."""
        return f"https://www.fca.org.uk/publications/consultation-papers/{self.cp_number.lower().replace('/', '-')}"
    
    @computed_field
    @property
    def document_uri(self) -> str:
        return f"consultation_paper_{self.cp_number.replace('/', '_')}"


class FCAAuthorisedFirm(ElasticDocument):
    """Model for FCA Authorised Firms from the Financial Services Register."""
    
    model_config = ConfigDict(extra="forbid")
    
    # Core identification
    firm_reference_number: str  # FRN - Primary identifier
    firm_name: str
    trading_names: list[str] = []
    
    # Status and regulatory information
    firm_status: str  # "Authorised", "EEA Authorised", etc.
    sub_status: str | None = None  # "In Administration", etc.
    business_type: str | None = None  # "Regulated", "PSD", etc.
    status_effective_date: str | None = None
    
    # Corporate information
    companies_house_number: str | None = None
    mutual_society_number: str | None = None
    
    # Address information (comprehensive)
    address_line_1: str | None = None
    address_line_2: str | None = None
    address_line_3: str | None = None
    address_line_4: str | None = None
    city: str | None = None
    county: str | None = None
    postcode: str | None = None
    country: str | None = None
    
    # Contact information
    telephone: str | None = None
    website: str | None = None
    email: str | None = None
    
    # Regulatory permissions and restrictions
    permissions: list[str] = []  # Detailed permissions from /Permissions endpoint
    regulatory_requirements: list[str] = []  # From /Requirements endpoint
    limitations: list[str] = []  # Extracted from permissions
    client_money_permission: str | None = None
    
    # PSD/EMD information
    psd_status: str | None = None  # PSD/EMD status
    psd_effective_date: str | None = None
    e_money_agent_status: str | None = None
    e_money_agent_effective_date: str | None = None
    psd_agent_status: str | None = None
    psd_agent_effective_date: str | None = None
    
    # MLR information
    mlrs_status: str | None = None
    mlrs_status_effective_date: str | None = None
    
    # People and governance
    key_individuals: list[str] = []  # Names from /Individuals endpoint
    senior_managers: list[dict] = []  # From /CF endpoint (controlled functions)
    
    # Regulatory history and compliance
    disciplinary_history: list[str] = []  # From /DisciplinaryHistory endpoint
    regulatory_requirements_details: list[dict] = []  # Structured requirements data
    waivers: list[str] = []  # From /Waivers endpoint
    exclusions: list[str] = []  # From /Exclusions endpoint
    
    # Business relationships
    appointed_representatives: int = 0
    ar_relationships: list[dict] = []  # From /AR endpoint
    regulators: list[dict] = []  # From /Regulators endpoint
    passports: list[dict] = []  # From /Passports endpoint
    
    # Exceptional information and warnings
    exceptional_info: list[str] = []  # Important notices/warnings
    
    # Administrative data
    authorisation_date: datetime | None = None
    search_term: str | None = None  # Track which search term found this firm
    last_updated: datetime = Field(default_factory=datetime.now)
    
    @computed_field
    @property
    def register_url(self) -> str:
        """Generate URL to the FCA Register entry."""
        return f"https://register.fca.org.uk/ShPo_FirmDetailsPage?id={self.firm_reference_number}"
    
    @computed_field
    @property
    def document_uri(self) -> str:
        return f"firm_{self.firm_reference_number}"


class FCAEnforcementNotice(ElasticDocument):
    """Model for FCA Enforcement Notices."""
    
    model_config = ConfigDict(extra="forbid")
    
    notice_id: str
    firm_individual_name: str
    firm_reference_number: str | None = None  # FRN
    notice_type: str  # "Final Notice", "Decision Notice", "Warning Notice"
    publication_date: datetime
    action_date: datetime | None = None
    summary: str | None = None
    content: str
    financial_penalty: str | None = None
    regulatory_breaches: list[str] = []
    outcome: str | None = None
    source_url: str | None = None
    
    @computed_field
    @property
    def enforcement_url(self) -> str:
        """Generate URL to the enforcement notice."""
        return f"https://www.fca.org.uk/news/{self.notice_id}"
    
    @computed_field
    @property
    def document_uri(self) -> str:
        return f"enforcement_{self.notice_id}"


# Response models for FCA API endpoints
class FCAHandbookResponse(BaseModel):
    """API response model for FCA Handbook searches."""
    
    results: list[FCAHandbookSection]
    total_results: int
    
    model_config = ConfigDict(extra="ignore")


class FCAPolicyResponse(BaseModel):
    """API response model for FCA Policy documents."""
    
    results: list[FCAPolicyStatement | FCAConsultationPaper]
    total_results: int
    
    model_config = ConfigDict(extra="ignore")


class FCAFirmResponse(BaseModel):
    """API response model for FCA Authorised Firms."""
    
    results: list[FCAAuthorisedFirm]
    total_results: int
    
    model_config = ConfigDict(extra="ignore")


class FCAIndividual(ElasticDocument):
    """Model for FCA Individual Register data."""
    
    model_config = ConfigDict(extra="forbid")
    
    # Core identification
    individual_reference_number: str  # IRN - Primary identifier
    full_name: str
    commonly_used_name: str | None = None
    
    # Status information
    individual_status: str  # "Active", "Approved by regulator", etc.
    status_effective_date: str | None = None
    
    # Current and historical roles
    current_roles: list[dict] = []  # Current controlled functions
    previous_roles: list[dict] = []  # Historical controlled functions
    
    # Workplace information
    workplace_locations: list[dict] = []  # Geographic locations where they work
    
    # Regulatory history
    disciplinary_history: list[dict] = []  # From /DisciplinaryHistory endpoint
    regulatory_approvals: list[str] = []
    
    # Administrative data
    last_updated: datetime = Field(default_factory=datetime.now)
    
    @computed_field
    @property
    def register_url(self) -> str:
        """Generate URL to the FCA Register entry."""
        return f"https://register.fca.org.uk/ShPo_IndividualDetailsPage?id={self.individual_reference_number}"
    
    @computed_field
    @property
    def document_uri(self) -> str:
        return f"individual_{self.individual_reference_number}"


class FCAProduct(ElasticDocument):
    """Model for FCA Collective Investment Schemes (Products)."""
    
    model_config = ConfigDict(extra="forbid")
    
    # Core identification
    product_reference_number: str  # PRN - Primary identifier
    product_name: str
    other_names: list[dict] = []  # Historical names with effective dates
    
    # Product information
    product_type: str | None = None  # "Offshore OEIC", etc.
    scheme_type: str | None = None  # "Offshore", "Authorised", etc.
    status: str  # "Recognised", "Authorised", etc.
    effective_date: str | None = None
    
    # Management information
    operator_name: str | None = None
    operator_frn: str | None = None
    cis_depositary_name: str | None = None
    cis_depositary_frn: str | None = None
    
    # Product structure
    subfunds: list[dict] = []  # From /Subfund endpoint
    mmf_nav_type: str | None = None  # Money Market Fund NAV type
    mmf_term_type: str | None = None  # Money Market Fund term type
    
    # Registration information
    icvc_registration_number: str | None = None
    
    # Administrative data
    last_updated: datetime = Field(default_factory=datetime.now)
    
    @computed_field
    @property
    def register_url(self) -> str:
        """Generate URL to the FCA Register entry."""
        return f"https://register.fca.org.uk/ShPo_ProductDetailsPage?id={self.product_reference_number}"
    
    @computed_field
    @property
    def document_uri(self) -> str:
        return f"product_{self.product_reference_number}"
