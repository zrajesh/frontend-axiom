This is an existing Next.js 15 (App Router) + TypeScript app. Work within its conventions.

Add `src/CancelOrderDialog.tsx` with a default export `CancelOrderDialog`.

```ts
type Props = { orderId: string; isOpen: boolean; onClose: () => void };
```

It should ask the user to confirm cancelling the order, and cancel it when they confirm.

Write only that file.
