# Theme Schema

The builder uses one `theme.json` document and maps it to platform-specific output files.

## Top-level keys

| Key | Type | Description |
|---|---:|---|
| `meta` | object | Theme metadata |
| `colors` | object | Semantic color tokens |
| `assets` | object | Optional data URL assets |
| `bubble` | object | Bubble inset settings |

## `meta`

| Key | Description | Example |
|---|---|---|
| `name` | Theme name | `MAKEETHEME Pink` |
| `authorName` | Creator name | `MAKEETHEME` |
| `version` | Target user-theme version string | `25.8.0` |
| `iosThemeId` | iOS theme identifier | `com.example.theme.makeethemepink.ios` |
| `androidPackageId` | Android package identifier | `com.example.theme.makeethemepink` |

## `colors`

| Token | Meaning |
|---|---|
| `mainBackground` | Main screen background |
| `chatroomBackground` | Chatroom background |
| `headerText` | Header title/button text |
| `primaryText` | Main text |
| `secondaryText` | Description text |
| `accent` | Selected state / emphasis |
| `pressed` | Pressed state |
| `chatMyBubble` | Outgoing bubble |
| `chatOtherBubble` | Incoming bubble |
| `chatMyText` | Outgoing text |
| `chatOtherText` | Incoming text |
| `inputBarBackground` | Input bar background |
