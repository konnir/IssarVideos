"""
Narrative Explanation Module

This module uses the LLM client to explain English narratives in Hebrew.
It provides functionality to translate and explain narrative concepts 
in a clear, comprehensive Hebrew paragraph.
"""

import logging
from typing import Dict, Any, Optional
from clients.openai_client import OpenAIClient

# Set up logging
logger = logging.getLogger(__name__)


class NarrativeExplainer:
    """Explain English narratives in Hebrew using LLM."""

    def __init__(self, openai_client: Optional[OpenAIClient] = None):
        """
        Initialize the narrative explainer.

        Args:
            openai_client: Optional OpenAI client instance. If None, creates a new one.
        """
        self.openai_client = openai_client or OpenAIClient()

    def explain_narrative(self, narrative: str) -> Dict[str, Any]:
        """
        Explain an English narrative in Hebrew.

        Args:
            narrative: The English narrative to explain

        Returns:
            Dictionary containing:
            - narrative_hebrew: Hebrew translation of the narrative
            - explanation_hebrew: Hebrew explanation paragraph

        Raises:
            Exception: If explanation generation fails
        """
        try:
            # Create system prompt for combined translation and explanation
            system_prompt = self._create_combined_system_prompt()

            # Create user prompt with the narrative
            user_prompt = self._create_combined_user_prompt(narrative)

            # Generate both translation and explanation in a single API call
            response = self.openai_client.generate_simple_completion(
                prompt=user_prompt,
                system_prompt=system_prompt,
                temperature=0.7,  # Balanced creativity and accuracy
                max_tokens=400,   # Enough for both translation and explanation
            )

            # Parse the response to extract translation and explanation
            result = self._parse_combined_response(response.strip())
            
            return {
                "narrative_hebrew": result["narrative_hebrew"],
                "explanation_hebrew": result["explanation_hebrew"]
            }

        except Exception as e:
            logger.error(f"Narrative explanation failed: {str(e)}")
            raise Exception(f"Failed to explain narrative: {str(e)}")

    def _create_combined_system_prompt(self) -> str:
        """Create the system prompt for combined Hebrew translation and explanation."""
        
        return """אתה מתרגם ומסביר מושגים מומחה בעברית. המשימה שלך היא לקבל נרטיב באנגלית ולספק:
1. תרגום מדויק לעברית
2. הסבר מפורט בעברית

פורמט התגובה:
תרגום: [התרגום בעברית]
הסבר: [הסבר מפורט בעברית]

הנחיות:
- תרגם את הנרטיב באופן מדויק וטבעי לעברית
- הסבר את המשמעות העמוקה של הנרטיב בפסקה ברורה ומקיפה
- כתב בעברית תקנית וזורמת
- ספק הקשר תרבותי או חברתי אם רלוונטי
- שמור על אורך של פסקה אחת בהסבר (3-5 משפטים)
- הקפד על בהירות ונגישות לקורא עברי

דוגמה:
נרטיב באנגלית: "Career pivoting as personal growth"
תרגום: מעבר קריירה כצמיחה אישית
הסבר: מעבר קריירה כצמיחה אישית מתייחס לתהליך שבו אדם בוחר לשנות את נתיב הקריירה שלו לא רק מסיבות כלכליות או מקצועיות, אלא כחלק מתהליך של התפתחות אישית עמוקה יותר. הנרטיב הזה מציג את שינוי הקריירה כהזדמנות לגילוי עצמי, למימוש פוטנציאל חדש ולהתמודדות עם אתגרים שמובילים לבגרות רגשית ומקצועית.

החזר את התשובה בפורמט הנדרש בלבד."""

    def _create_combined_user_prompt(self, narrative: str) -> str:
        """Create the user prompt for combined translation and explanation."""
        
        return f"""נרטיב באנגלית: "{narrative}"

אנא תרגם והסבר את הנרטיב הזה בעברית בפורמט הנדרש."""

    def _parse_combined_response(self, response: str) -> Dict[str, str]:
        """Parse the combined response to extract translation and explanation."""
        
        try:
            # Split the response by lines and look for the format
            lines = response.split('\n')
            narrative_hebrew = ""
            explanation_hebrew = ""
            
            for line in lines:
                line = line.strip()
                if line.startswith('תרגום:'):
                    narrative_hebrew = line[len('תרגום:'):].strip()
                elif line.startswith('הסבר:'):
                    explanation_hebrew = line[len('הסבר:'):].strip()
            
            # If parsing fails, try alternative approach
            if not narrative_hebrew or not explanation_hebrew:
                # Look for the pattern in the entire response
                import re
                translation_match = re.search(r'תרגום:\s*(.+?)(?=\n.*הסבר:|$)', response, re.DOTALL)
                explanation_match = re.search(r'הסבר:\s*(.+)', response, re.DOTALL)
                
                if translation_match:
                    narrative_hebrew = translation_match.group(1).strip()
                if explanation_match:
                    explanation_hebrew = explanation_match.group(1).strip()
            
            # Fallback: if still no proper parsing, use the whole response as explanation
            if not narrative_hebrew and not explanation_hebrew:
                # Try to split by common patterns
                parts = response.split('תרגום:')
                if len(parts) > 1:
                    rest = parts[1].split('הסבר:')
                    if len(rest) > 1:
                        narrative_hebrew = rest[0].strip()
                        explanation_hebrew = rest[1].strip()
                    else:
                        narrative_hebrew = rest[0].strip()
                        explanation_hebrew = response
                else:
                    # Last resort: use response as explanation
                    narrative_hebrew = "תרגום לא זמין"
                    explanation_hebrew = response
            
            return {
                "narrative_hebrew": narrative_hebrew,
                "explanation_hebrew": explanation_hebrew
            }
            
        except Exception as e:
            logger.error(f"Failed to parse combined response: {str(e)}")
            # Return the original response as explanation if parsing fails
            return {
                "narrative_hebrew": "תרגום לא זמין",
                "explanation_hebrew": response
            }

# Convenience function for quick narrative explanation
def explain_narrative_in_hebrew(narrative: str) -> Dict[str, Any]:
    """
    Convenience function to quickly explain a narrative in Hebrew.

    Args:
        narrative: The English narrative to explain

    Returns:
        Dictionary with Hebrew explanation
    """
    explainer = NarrativeExplainer()
    return explainer.explain_narrative(narrative)
