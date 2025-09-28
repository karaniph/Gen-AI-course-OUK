import:py os;
import:py byllm;

glob llm = byllm.Model(model_name=os.getenv("JAC_MODEL", "gemini/gemini-2.5-flash"));

def simple_chat(message: str) -> str by llm;

sem simple_chat = """
Respond to the user's message in a friendly and helpful way.
Keep responses concise and conversational.
""";

with entry {
    print("=== Testing AI Integration ===");
    
    try {
        response = simple_chat("Hello! Can you tell me a fun fact?");
        print("AI:", response);
        print("SUCCESS: AI integration is working!");
    } catch e {
        print("ERROR:", str(e));
        print("AI integration failed - check byllm installation and API keys");
    }
}
