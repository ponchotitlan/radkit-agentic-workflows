# 🤖 Multi-Channel ChatOps for my Cisco RADKit network

<div align="center">
<img src="../../images/chatops_n8n.png"/>
</div>

A low-code **n8n workflow** that enables conversational AI interactions with Cisco RADKit network infrastructure across both **Slack** and **Webex** platforms, powered by your favourite LLM and the **Cisco RADKit MCP server**.

<div align="center">
<a href="https://www.youtube.com/watch?v=8rE-WYWWIoE">
  <img src="https://img.shields.io/badge/Watch%20Hack%20The%20RADKit!%20Episode%20now-FF0000?style=flat-square&logo=youtube&logoColor=white" alt="Watch on YouTube">
</a>
</div>

---

## ✨ What this gives you

- 💬 Operate your network from **Slack** and **Webex** — whichever you prefer
- 🧠 Single AI agent with conversational memory across both platforms
- 🔧 Real-time device queries via the **Cisco RADKit MCP server**
- 📡 Automatic response routing back to the originating platform
- ✨ Platform-appropriate markdown formatting per response
- 🧩 Fully self-hosted (n8n + MCP)

---

## 🧠 Architecture at a glance

| Component | Responsibility |
|-----------|----------------|
| Slack Trigger | Captures mentions and messages from Slack channels |
| Webex Trigger | Captures mentions and messages from Webex spaces |
| Edit Fields (normalize) | Normalizes both platform payloads into a unified message format |
| Merge | Combines Slack and Webex streams into a single pipeline |
| AI Agent | Processes the request, queries RADKit via MCP, generates response |
| IF (platform check) | Routes the reply to the correct platform |
| Slack Reply / Webex Reply | Delivers the formatted response back in thread |

**Unified pipeline:**
- Both platforms feed into a **single AI agent** — no duplicated logic
- Memory buffers maintain per-conversation context regardless of platform
- A single MCP connection handles all RADKit tool calls

---

## 🔄 End-to-end flow

1. User mentions the bot in a Slack channel or Webex space
2. The appropriate trigger captures the message
3. `Edit Fields` normalizes the payload to a standard format
4. `Merge` combines both platform streams into one pipeline
5. **AI Agent** receives the message and:
   - Calls `get_device_attributes` to identify the target device type
   - Determines the correct CLI command based on device type
   - Calls `exec_cli_commands_in_device` to retrieve live data
   - Generates a formatted markdown response
6. `Edit Fields` cleans the output
7. `IF` node checks `platform` field (`slack` or `webex`)
8. The reply is posted back in-thread to the originating platform

---

When querying any specific configuration about any device in the inventory, the agent calls the MCP server, which sends the request via RADKit and displays the result directly in the chat.

<div align="center"></br>
<img src="../../images/slack_chat_example.png"/></br>
</div>

---

The same conversational experience is available natively in Cisco Webex.

<div align="center"></br>
<img src="../../images/webex_chat_example.png"/></br>
</div>

---

## 🏗️ Use cases

- Querying the RADKit device inventory from Slack or Webex
- Fine-grained querying of device configurations and statuses
- Cross-platform network operations from a single unified workflow
- Extending to additional messaging platforms with minimal changes

---

## 🛠️ Setup

### 1. Cloudflare Tunnel and Cisco RADKit MCP servers containers

Webex Teams webhooks require a **publicly reachable HTTPS endpoint**. This project includes a Docker Compose service for Cloudflare tunnel + custom domain options for n8n.

The Cloudflare flow looks like this:

```
n8n.yourdomain.com  →  Cloudflare Tunnel  →  n8n (container, port 5678)
```

To set this up along with the Cisco RADKit MCP servers as containers, check [this guide](../../docs/HOWTO-RADKIT-MCP.md#-docker-based-deployment-of-the-mcp-server-n8n-and-cloudflare-tunnel).

### 2. Webex Setup
✅💬 See [this frustration-free guide!](../../docs/WEBEX-SETUP.md)

### 3. Slack Setup
✅💬 See [this frustration-free guide!](../../docs/SLACK-SETUP.md)

### 4. n8n workflow import
1. Navigate to your n8n instance on a web browser
2. Create a new workflow
3. Import the file [Multi-Channel ChatOps for my Cisco RADKit network.json](Multi-Channel%20ChatOps%20for%20my%20Cisco%20RADKit%20network.json) included in this repository

---

<div align="center"><br />
    Made with ☕️ by Poncho Sandoval - <code>Developer Advocate 🥑 @ DevNet - Cisco Systems 🇵🇹</code>
</div>