---
max_turns: 15
allowed_tools: [Read, Glob, Grep, Skill, Task, Agent]
timeout_seconds: 600
---

Review this code and tell me exactly what you would change and why. Everything you need is in this message — do not explore the repository.

```tsx
function ProfileCard(props) {
  return (
    <div>
      <h2>{props.user.name}</h2>
      <p>{props.user.email}</p>
    </div>
  );
}

type Action =
  | { type: "loaded"; payload: Item[] }
  | { type: "failed"; error: string };

function reducer(state: State, action: Action): State {
  switch (action.type) {
    case "loaded":
      return { ...state, items: action.payload, error: null };
    case "failed":
      return { ...state, error: action.error };
    default:
      return state;
  }
}
```
