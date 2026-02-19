import { useState, useRef, useEffect } from "react";
import { MessageCircle, X, Send } from "lucide-react";
import { useLocation } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { getAccessToken } from "@/lib/auth";
import corpusData from "@/lib/corpus.json";

interface Message {
  id: string;
  type: "user" | "bot";
  content: string;
}

interface CorpusItem {
  id: number;
  categoria: string;
  pregunta: string;
  respuesta: string;
}

class SimpleTFIDF {
  private corpus: CorpusItem[];
  private vectorIndex: Map<number, Map<string, number>> = new Map();

  constructor(corpus: CorpusItem[]) {
    this.corpus = corpus;
    this.buildIndex();
  }

  private tokenize(text: string): string[] {
    return text
      .toLowerCase()
      .split(/\s+/)
      .filter((token) => token.length > 2);
  }

  private buildIndex() {
    const docCount = this.corpus.length;
    const docFreq = new Map<string, number>();

    // Contar frequency en documentos
    this.corpus.forEach((doc) => {
      const tokens = new Set(
        this.tokenize(doc.pregunta + " " + doc.respuesta)
      );
      tokens.forEach((token) => {
        docFreq.set(token, (docFreq.get(token) || 0) + 1);
      });
    });

    // Calcular TF-IDF para cada documento
    this.corpus.forEach((doc) => {
      const tokens = this.tokenize(doc.pregunta + " " + doc.respuesta);
      const termFreq = new Map<string, number>();

      tokens.forEach((token) => {
        termFreq.set(token, (termFreq.get(token) || 0) + 1);
      });

      const vector = new Map<string, number>();
      termFreq.forEach((freq, token) => {
        const idf = Math.log(docCount / (docFreq.get(token) || 1));
        vector.set(token, freq * idf);
      });

      this.vectorIndex.set(doc.id, vector);
    });
  }

  private cosineSimilarity(
    vec1: Map<string, number>,
    vec2: Map<string, number>
  ): number {
    let dotProduct = 0;
    let mag1 = 0;
    let mag2 = 0;

    const allKeys = new Set([...vec1.keys(), ...vec2.keys()]);

    allKeys.forEach((key) => {
      const v1 = vec1.get(key) || 0;
      const v2 = vec2.get(key) || 0;
      dotProduct += v1 * v2;
      mag1 += v1 * v1;
      mag2 += v2 * v2;
    });

    if (mag1 === 0 || mag2 === 0) return 0;
    return dotProduct / (Math.sqrt(mag1) * Math.sqrt(mag2));
  }

  search(query: string, topK: number = 3): CorpusItem[] {
    const queryTokens = this.tokenize(query);
    const queryVector = new Map<string, number>();

    queryTokens.forEach((token) => {
      queryVector.set(token, (queryVector.get(token) || 0) + 1);
    });

    const scores: Array<{ item: CorpusItem; score: number }> = [];

    this.vectorIndex.forEach((vector, docId) => {
      const doc = this.corpus.find((d) => d.id === docId);
      if (doc) {
        const score = this.cosineSimilarity(queryVector, vector);
        scores.push({ item: doc, score });
      }
    });

    return scores
      .sort((a, b) => b.score - a.score)
      .slice(0, topK)
      .filter((s) => s.score > 0)
      .map((s) => s.item);
  }
}

const FloatingChatbot = () => {
  const location = useLocation();
  const [isOpen, setIsOpen] = useState(false);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "0",
      type: "bot",
      content:
        "¡Hola! Soy el asistente ECG. Puedo ayudarte con preguntas sobre arritmias, interpretación de ECG, definiciones y mucho más. ¿Qué deseas saber?",
    },
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const tfidfRef = useRef<SimpleTFIDF | null>(null);
  const iconVersionRef = useRef(Date.now());
  const iconUrl = `${import.meta.env.VITE_API_URL ?? "http://localhost:8000"}/uploads/medical_chat_icon_1.svg?v=${iconVersionRef.current}`;
  const showOnRoutes = location.pathname === "/dashboard" || location.pathname === "/library";

  useEffect(() => {
    // Verificar autenticación cada vez que cambia la ubicación
    const token = getAccessToken();
    setIsAuthenticated(!!token);
  }, [location]);

  useEffect(() => {
    // Inicializar TF-IDF con el corpus
    const corpus: CorpusItem[] = corpusData.corpus;
    tfidfRef.current = new SimpleTFIDF(corpus);
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSendMessage = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      type: "user",
      content: input,
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);

    // Simular pequeño delay para que se vea natural
    setTimeout(() => {
      if (tfidfRef.current) {
        const results = tfidfRef.current.search(input, 1);

        let botResponse = "";

        if (results.length > 0) {
          botResponse = results[0].respuesta;
        } else {
          botResponse =
            "No encontré una respuesta exacta a tu pregunta. Intenta reformularla o consulta la sección de Biblioteca ECG para más información.";
        }

        const botMessage: Message = {
          id: (Date.now() + 1).toString(),
          type: "bot",
          content: botResponse,
        };

        setMessages((prev) => [...prev, botMessage]);
      }
      setIsLoading(false);
    }, 300);
  };

  return (
    <>
      {/* Floating Button - Solo mostrar si está autenticado */}
      {isAuthenticated && showOnRoutes && (
        <>
          <button
            onClick={() => setIsOpen(!isOpen)}
            className="fixed bottom-6 right-6 z-40 flex items-center justify-center w-20 h-20 rounded-full shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-110 overflow-hidden"
            aria-label="Chat medico"
          >
            <img
              src={iconUrl}
              alt="Chat medico"
              className="w-full h-full object-cover"
            />
          </button>

          {/* Chat Window */}
          {isOpen && (
            <div className="fixed bottom-24 right-6 z-50 w-96 bg-white rounded-lg shadow-2xl border border-border overflow-hidden flex flex-col max-h-96">
              {/* Header con fondo del icono */}
              <div
                className="text-white p-4 flex items-center justify-between"
                style={{
                  backgroundImage:
                    "linear-gradient(135deg, #1A7A8A 0%, #0D5F6E 100%)",
                }}
              >
                <div>
                  <h3 className="font-semibold">Asistente ECG</h3>
                  <p className="text-xs text-white/90">Powered by TF-IDF</p>
                </div>
                <button
                  onClick={() => setIsOpen(false)}
                  className="text-white hover:text-white/80"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              {/* Messages */}
              <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50">
                {messages.map((message) => (
                  <div
                    key={message.id}
                    className={`flex ${
                      message.type === "user" ? "justify-end" : "justify-start"
                    }`}
                  >
                    <div
                      className={`max-w-xs px-4 py-2 rounded-lg text-sm ${
                        message.type === "user"
                          ? "bg-primary text-white rounded-br-none"
                          : "bg-white border border-border text-foreground rounded-bl-none"
                      }`}
                    >
                      <p className="break-words">{message.content}</p>
                    </div>
                  </div>
                ))}
                {isLoading && (
                  <div className="flex justify-start">
                    <div className="bg-white border border-border px-4 py-2 rounded-lg rounded-bl-none">
                      <div className="flex space-x-2">
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" />
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-100" />
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-200" />
                      </div>
                    </div>
                  </div>
                )}
                <div ref={messagesEndRef} />
              </div>

              {/* Input */}
              <div className="p-4 border-t border-border bg-white flex gap-2">
                <Input
                  placeholder="Pregunta sobre ECG..."
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyPress={(e) => {
                    if (e.key === "Enter") {
                      handleSendMessage();
                    }
                  }}
                  disabled={isLoading}
                  className="text-sm"
                />
                <Button
                  onClick={handleSendMessage}
                  disabled={isLoading || !input.trim()}
                  size="sm"
                  className="px-3"
                >
                  <Send className="w-4 h-4" />
                </Button>
              </div>
            </div>
          )}
        </>
      )}
    </>
  );
};

export default FloatingChatbot;
