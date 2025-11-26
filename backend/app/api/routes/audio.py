from __future__ import annotations

import logging
import tempfile
from pathlib import Path

from fastapi import APIRouter, File, UploadFile, HTTPException, status
from fastapi.responses import StreamingResponse
from openai import OpenAI

from app.core.settings import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/audio", tags=["Audio"])

@router.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    """Transcribe uploaded audio file using OpenAI Whisper."""
    if not settings.OPENAI_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="OpenAI API key not configured",
        )

    client = OpenAI(api_key=settings.OPENAI_API_KEY)

    # Save uploaded file temporarily
    suffix = Path(file.filename).suffix if file.filename else ".webm"
    with tempfile.NamedTemporaryFile(delete=True, suffix=suffix) as temp_audio:
        content = await file.read()
        temp_audio.write(content)
        temp_audio.flush()
        
        try:
            # Transcribe
            with open(temp_audio.name, "rb") as audio_file:
                transcript = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    temperature=0,
                    prompt="User asking questions about retail store analytics. Languages: Malayalam, English, Manglish. Keywords: Sales, Stock, Staff, Performance, Best, Worst, Profit, Revenue. Malayalam examples: ആരാണ് മികച്ച സ്റ്റാഫ്? ഇന്നത്തെ വിൽപ്പന എത്ര? (Aaraanu mikacha staff? Innatha vilpana ethra?).",
                )
            
            return {"text": transcript.text}
            
        except Exception as e:
            logger.error("Transcription failed: %s", e, exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to transcribe audio",
            )

@router.post("/speak")
async def text_to_speech(text: str):
    """Convert text to speech using OpenAI TTS."""
    if not settings.OPENAI_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="OpenAI API key not configured",
        )
        
    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    
    try:
        response = client.audio.speech.create(
            model="tts-1",
            voice="alloy",
            input=text,
        )
        
        # Stream the audio back
        return StreamingResponse(
            response.iter_bytes(),
            media_type="audio/mpeg"
        )
        
    except Exception as e:
        logger.error("TTS failed: %s", e, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate speech",
        )
