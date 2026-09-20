Create `src/OrdersList.tsx` with a default export named `OrdersList`.

It receives this exact props contract — use it as given:

```ts
type Order = { id: string; reference: string; total: number };
type Props = {
  isLoading: boolean;
  isError: boolean;
  isFetching: boolean;
  orders: Order[];
  onRetry: () => void;
};
```

Render the customer's orders. This is a real screen that ships to users.
Write only that file.
