# Input Agent Implementation

## Overview

The Input Agent is responsible for parsing natural language input (text or voice) and extracting structured website requirements. It uses Google Gemini AI to understand user intent and can generate clarifying questions when requirements are incomplete or ambiguous.

## Features Implemented

### 1. Requirements Parsing
- Extracts structured requirements from natural language descriptions
- Supports both text and voice input types
- Uses Gemini AI with low temperature (0.2) for consistent extraction
- Validates completeness of extracted requirements

### 2. Clarifying Questions
- Detects incomplete or ambiguous requirements
- Generates specific, actionable clarifying questions using Gemini
- Handles follow-up responses to update requirements
- Maintains conversation context across multiple interactions

### 3. Conversation History
- Stores conversation history in Redis with 24-hour TTL
- Provides context for better requirement extraction
- Supports conversation retrieval and clearing

## Data Models

### SiteRequirements
```python
{
    "site_type": str,              # Required: portfolio, blog, landing page, etc.
    "pages": List[str],            # Optional: ["home", "about", "contact"]
    "color_palette": str,          # Optional: color scheme
    "key_features": List[str],     # Required: ["contact form", "gallery"]
    "design_style": str,           # Optional: modern, minimalist, etc.
    "target_audience": str,        # Optional: who the site is for
    "content_tone": str,           # Optional: professional, casual, etc.
    "additional_details": dict     # Optional: any other info
}
```

## API Endpoints

### POST /api/requirements/parse
Parse user input into structured requirements.

**Request:**
```json
{
    "raw_input": "I want a portfolio website with a contact form",
    "input_type": "text",
    "session_id": "uuid",
    "conversation_history": []  // Optional
}
```

**Response:**
```json
{
    "success": true,
    "requirements": {
        "site_type": "portfolio",
        "key_features": ["contact form"],
        ...
    },
    "needs_clarification": false,
    "clarifying_questions": [],
    "conversation_id": "uuid",
    "message": "Requirements parsed successfully"
}
```

### POST /api/requirements/clarify
Handle user response to clarifying questions.

**Request:**
```json
{
    "session_id": "uuid",
    "user_response": "I want a modern design with blue colors",
    "previous_requirements": {...},
    "conversation_history": []  // Optional
}
```

**Response:**
```json
{
    "success": true,
    "requirements": {
        "site_type": "portfolio",
        "design_style": "modern",
        "color_palette": "blue",
        ...
    },
    "needs_clarification": false,
    "clarifying_questions": [],
    "conversation_id": "uuid",
    "message": "Requirements updated successfully"
}
```

### GET /api/requirements/conversation/{session_id}
Retrieve conversation history for a session.

**Response:**
```json
{
    "session_id": "uuid",
    "conversation_history": [
        {
            "role": "user",
            "content": "I want a portfolio website",
            "timestamp": "2024-11-16T12:00:00Z"
        },
        {
            "role": "assistant",
            "content": "Extracted requirements: {...}",
            "timestamp": "2024-11-16T12:00:01Z"
        }
    ],
    "message": "Conversation history retrieved successfully"
}
```

### DELETE /api/requirements/conversation/{session_id}
Clear conversation history for a session.

**Response:**
```json
{
    "session_id": "uuid",
    "message": "Conversation history cleared successfully"
}
```

## Implementation Details

### Agent Class: InputAgent
- **Location:** `backend/agents/input_agent.py`
- **Inherits from:** `BaseAgent`
- **Dependencies:** 
  - `gemini_service` for LLM interactions
  - `redis_service` for conversation history storage

### Key Methods

#### `_parse_requirements(input_data, context)`
- Builds prompt with conversation history
- Calls Gemini with structured JSON schema
- Validates completeness of extracted requirements
- Generates clarifying questions if needed
- Stores conversation history in Redis

#### `_handle_clarification(input_data, context)`
- Processes user response to clarifying questions
- Updates requirements based on new information
- Re-checks completeness
- May generate additional questions if still incomplete

#### `_check_completeness(requirements)`
- Validates required fields: `site_type` and `key_features`
- Returns tuple of (is_complete, missing_info)
- Optional fields don't block completion

#### `_generate_clarifying_questions(requirements, missing_info, history)`
- Uses Gemini to generate 2-3 specific questions
- Focuses on most important missing information
- Falls back to predefined questions if LLM fails

### Validation

The agent validates outputs to ensure:
- Required fields are present (site_type, key_features)
- Clarifying questions are provided when needed
- Output format matches expected schema

### Error Handling

- **Validation Errors:** Return 400 with clear message
- **LLM Errors:** Return 503 with retry suggestion
- **Storage Errors:** Log warning, continue with degraded functionality
- All errors are logged with context for debugging

## Testing

To test the Input Agent:

1. **Setup environment:**
   ```bash
   cd backend
   make setup
   ```

2. **Start the API server:**
   ```bash
   make dev
   ```

3. **Test parsing endpoint:**
   ```bash
   curl -X POST http://localhost:8000/api/requirements/parse \
     -H "Content-Type: application/json" \
     -d '{
       "raw_input": "I want a portfolio website with a contact form and image gallery",
       "input_type": "text",
       "session_id": "550e8400-e29b-41d4-a716-446655440000"
     }'
   ```

4. **Test clarification endpoint:**
   ```bash
   curl -X POST http://localhost:8000/api/requirements/clarify \
     -H "Content-Type: application/json" \
     -d '{
       "session_id": "550e8400-e29b-41d4-a716-446655440000",
       "user_response": "I want a modern design with blue colors",
       "previous_requirements": {
         "site_type": "portfolio",
         "key_features": ["contact form", "image gallery"]
       }
     }'
   ```

## Configuration

Required environment variables:
- `GEMINI_API_KEY`: Google Gemini API key
- `REDIS_URL`: Redis connection URL
- `SESSION_TTL_HOURS`: Session TTL in hours (default: 24)

## Integration with Workflow

The Input Agent is the first agent in the CREATE_SITE workflow:

1. User provides natural language description
2. Input Agent extracts structured requirements
3. If incomplete, returns clarifying questions
4. User responds to questions
5. Input Agent updates requirements
6. Once complete, requirements are passed to Code Generation Agent

## Future Enhancements

- Support for voice transcription (currently expects pre-transcribed text)
- Multi-language support
- Learning from user preferences over time
- Integration with template library for better suggestions
- Confidence scoring for extracted requirements
