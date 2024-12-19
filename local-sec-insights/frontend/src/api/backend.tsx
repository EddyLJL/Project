import { backendUrl } from "~/config";
import type { Message } from "~/types/conversation";
import type { BackendDocument } from "~/types/backend/document";
import { SecDocument } from "~/types/document";
import { fromBackendDocumentToFrontend } from "./utils/documents";

interface CreateConversationPayload {
  id: string;
}

interface GetConversationPayload {
  id: string;
  messages: Message[];
  documents: BackendDocument[];
}

interface GetConversationReturnType {
  messages: Message[];
  documents: SecDocument[];
}

class BackendClient {
  private baseUrl: string;

  constructor() {
    this.baseUrl = backendUrl?.endsWith('/') ? backendUrl : backendUrl + '/';
    console.log('Backend URL:', this.baseUrl);
  }

  private async get(endpoint: string) {
    try {
      const cleanEndpoint = endpoint.startsWith('/') ? endpoint.slice(1) : endpoint;
      const url = `${this.baseUrl}${cleanEndpoint}`;
      console.log('Fetching:', url);
      const response = await fetch(url);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return response;
    } catch (error) {
      console.error('API request failed:', error);
      throw error;
    }
  }

  private async post(endpoint: string, body?: any) {
    const url = backendUrl + endpoint;
    const res = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });

    if (!res.ok) {
      throw new Error(`HTTP error! status: ${res.status}`);
    }
    return res;
  }

  public async createConversation(documentIds: string[]): Promise<string> {
    const endpoint = "api/conversation/";
    const payload = { document_ids: documentIds };
    const res = await this.post(endpoint, payload);
    const data = (await res.json()) as CreateConversationPayload;

    return data.id;
  }

  public async fetchConversation(
    id: string
  ): Promise<GetConversationReturnType> {
    const endpoint = `api/conversation/${id}`;
    const res = await this.get(endpoint);
    const data = (await res.json()) as GetConversationPayload;

    return {
      messages: data.messages,
      documents: fromBackendDocumentToFrontend(data.documents),
    };
  }

  public async fetchDocuments(): Promise<SecDocument[]> {
    try {
      const endpoint = 'api/document';
      const res = await this.get(endpoint);
      const data = await res.json();
      return fromBackendDocumentToFrontend(data);
    } catch (error) {
      console.error('Could not fetch documents:', error);
      return [];
    }
  }
}

export const backendClient = new BackendClient();
