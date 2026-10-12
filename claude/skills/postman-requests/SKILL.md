---
name: postman-requests
description: Add or update the requests of the endpoints I developed in my Postman collection "Hyros private", following its folder layout, naming, variables and descriptions. Use when asked to create, register or document endpoints in Postman, to add a saved example response, or to build a run-in-order scenario folder for a card.
---

# Postman requests

Put the endpoints of a card into my Postman collection through the Postman MCP,
laid out exactly like the requests already there. Load `postman:postman-knowledge`
first for the tool list and its limitations.

## The collection

| What | Value |
| --- | --- |
| Collection | `Hyros private`, uid `33209394-bf2cedd0-962c-479a-b2ef-ec9ff2c9fb5a` |
| Workspace | `My Workspace` |
| Auth | Bearer `{{hyrosAccessToken}}` at collection level, refreshed by a pre-request script against `{{hyrosBackendUrl}}/sessions/refresh` |

The ids below were right when this was written. If a call fails with a not found
error, read the tree again with `getCollection` and use what it returns.

| Area folder | Folder id | Holds the controllers of | Base URL variable |
| --- | --- | --- | --- |
| `AIR` | `4101488a-029a-446d-986e-f4c919d6b296` | `hyros-air-backend` | `{{airBaseUrl}}` |
| `Backend Internal` | `1dbb48bc-2a5a-44bd-8d72-9132d24a686c` | `hyros-backend-internal` | `{{hyrosBackendUrl}}` |
| `Backend Public` | `5e02af66-186e-42f2-b48d-cdc097c6a819` | `hyros-backend-public`, `/api/v1.0` | `{{hyrosBackendUrl}}` |
| `Tracking` | `39fca90d-eafa-ca56-8f94-44b4a36d2a1a` | `hyros-tracking` | `{{hyrosTrackingUrl}}` |

The other top-level folders (`ADMIN`, `Settings`, `Clicks`, `Revenue` and the
rest) are legacy. Never add to them.

## Layout

```
Hyros private
└── <Area folder>
    ├── <ControllerClassName>
    │   ├── <javaMethodName>
    │   └── <javaMethodName> - <scenario>
    └── <CARD-KEY> <short description> (run in order)
        ├── 1. <step in lowercase>
        └── 2. <step in lowercase>
```

- **Controller folder.** Named exactly like the Java class that holds the
  endpoint, such as `AirSuperAdminResource`, `LeadResource` or `SdrChatController`.
  Reuse it when it exists. Create it inside the area folder when it does not.
  When I name a different folder, use mine.
- **Request name.** The Java method name, as is: `getAgentFlowStats`,
  `forceStopBlockedFlows`.
- **Variant of the same endpoint.** `<method> - <scenario>`, such as
  `getSalesStatsForCustomers - 3 tags (control)`.
- **Scenario folder.** Only when I ask for a flow that has to run in order. It is
  named `<KEY> <short description> (run in order)`, and its requests are
  `N. <step>` in lowercase.

## Building each request

Read the controller before writing anything. The URL, the headers and the body
come from the code, never from memory.

- **URL.** Base variable of the area, then the class mapping, then the method
  mapping. For example, `@RequestMapping("/air/superadmin")` with
  `@GetMapping("/openrouter-provider-blacklist")` gives
  `{{airBaseUrl}}/air/superadmin/openrouter-provider-blacklist`. Path variables
  go as `{{name}}`, such as `{{agentExternalId}}`.
- **Query parameters.** Fill `queryParams` and repeat them in the URL. Give each
  one a short description. A required one gets an example value and
  `enabled: true`. An optional one is left empty with `enabled: false`, and its
  description says what happens when it is missing.
- **Headers.** Only the ones the method reads. Use these values and descriptions:

  | Header | Value | Description |
  | --- | --- | --- |
  | `productId` | `{{productId}}` | `Product ID (request header)` |
  | `userId` | `{{userId}}` | `User ID (request header)` |
  | `Content-Type` | `application/json` | only when there is a body |
  | `API-Key` | `{{apiKey}}` | public API only |
  | `Product-ID` | `{{productId}}` | tracking only |

- **Auth.** Leave it out so the request inherits the collection bearer. Set
  `noauth` only on public API (`API-Key`) and tracking requests.
- **Body.** `dataMode: raw`, `dataOptions.raw.language: json`, a realistic
  example built from the request DTO, and variables where a value repeats.
- **Description.** English prose, no em dashes.
  - The first sentence says who can call it, such as `SUPER_ADMIN only.`, and
    what it does.
  - Then explain the parameters that are not obvious, the possible outcomes or
    status codes, and anything surprising about the behaviour.
  - Keep it to what someone needs in order to call it correctly.

## Calling the MCP

- `createCollectionRequest` takes the collection uid and, in `folder`, the folder
  id without the `33209394-` owner prefix.
- `updateCollectionRequest` takes the bare collection id
  (`bf2cedd0-962c-479a-b2ef-ec9ff2c9fb5a`), not the uid.
- A request cannot be moved between folders. To move one, create it in the new
  folder, and ask before deleting the old one.
- Create requests one at a time, in the order they should appear. Parallel calls
  shuffle them.

## Saved responses

Only from a real call. Never invent an example. When I share a response or ask
you to run the endpoint locally, save it with `createCollectionResponse`, named
after the case it shows, such as `Agent - Flow With purchase copy`.

## Scenario folders

- Each step's description starts with `Step N of M.` and explains why the step
  exists.
- Steps pass values to each other through collection variables
  (`pm.collectionVariables.set`). Each step checks its own result with
  `pm.test`, and every assertion carries a message.

## Limits

- Never delete or rename an existing request, folder or variable without asking.
- Do not send requests to any server. Only build them.
- Do not touch the collection auth or its pre-request script.

## When done

Report a table with the folder, request name, method and URL of everything
created or changed, plus anything left out and why, such as missing example
responses.
