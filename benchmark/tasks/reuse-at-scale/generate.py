#!/usr/bin/env python3
"""
Generates the existing/ codebase for the reuse-at-scale task.

Why generated rather than hand-written: the point of this task is SCALE. The
earlier reuse fixture had three files, so Modal and Button were impossible to
miss and a capable model reused them with no help — delta 0.00. That measured
a condition real projects never have.

Here the pieces that must be reused are buried among ~45 components across
nested feature folders. Finding them costs real exploration, which is exactly
where model-native search degrades and a pre-computed index does not.

Deliberate choices:
  - The reusable primitives are NOT named after the task. Nothing called
    "ConfirmDialog" exists; the answer is `ui/Overlay` + `ui/ActionButton`,
    which only turn up by reading, not by guessing a filename.
  - Several near-miss decoys exist (`ui/Tooltip`, `ui/Drawer`, `feedback/Toast`)
    so "grep for the first dialog-ish thing" lands somewhere wrong.
  - The API module is `api/orders.ts` among eight other api modules.
"""

from __future__ import annotations

import os
import sys

UI_PRIMITIVES = {
    # The two that the task actually needs, named so they are not guessable.
    "Overlay": (
        'type OverlayProps = { isOpen: boolean; onDismiss: () => void; heading: string; '
        'children: React.ReactNode };\n'
        'export function Overlay({ isOpen, onDismiss, heading, children }: OverlayProps) {\n'
        '  if (!isOpen) return null;\n'
        '  return (\n'
        '    <div role="dialog" aria-modal="true" aria-label={heading}>\n'
        '      <h2>{heading}</h2>\n'
        '      {children}\n'
        '      <button type="button" onClick={onDismiss}>Dismiss</button>\n'
        '    </div>\n'
        '  );\n'
        '}\n'
    ),
    "ActionButton": (
        'type ActionButtonProps = { tone: "primary" | "destructive" | "quiet"; '
        'onPress: () => void; children: React.ReactNode; busy?: boolean };\n'
        'export function ActionButton({ tone, onPress, children, busy = false }: ActionButtonProps) {\n'
        '  return (\n'
        '    <button type="button" data-tone={tone} disabled={busy} onClick={onPress}>\n'
        '      {children}\n'
        '    </button>\n'
        '  );\n'
        '}\n'
    ),
}

# Decoys and filler. Near-misses first — these are what a shallow grep finds.
DECOYS = ["Tooltip", "Drawer", "Popover", "Sheet", "Banner", "Callout"]
FILLER_UI = [
    "Avatar", "Badge", "Breadcrumb", "Card", "Checkbox", "Chip", "Divider",
    "Dropdown", "EmptyState", "Field", "Icon", "Input", "Label", "Pagination",
    "ProgressBar", "RadioGroup", "Select", "Skeleton", "Spinner", "Stack",
    "Switch", "Table", "Tabs", "Textarea", "Thumbnail",
]
FEATURES = {
    "orders": ["OrderRow", "OrderStatusPill", "OrderTimeline", "OrderSummaryCard"],
    "billing": ["InvoiceRow", "PaymentMethodCard", "PlanBadge"],
    "settings": ["ProfileForm", "NotificationToggles"],
    "feedback": ["Toast", "InlineError"],
}
API_MODULES = {
    "orders": (
        "// Order operations. These are the only order endpoints that exist.\n"
        "export async function cancelOrder(orderId: string): Promise<void> {\n"
        '  await fetch(`/orders/${orderId}/cancel`, { method: "POST", credentials: "include" });\n'
        "}\n"
        "export async function getOrder(orderId: string) {\n"
        '  return fetch(`/orders/${orderId}`, { credentials: "include" }).then((r) => r.json());\n'
        "}\n"
    ),
    "billing": "export async function getInvoices() { return fetch('/invoices').then(r => r.json()); }\n",
    "settings": "export async function getProfile() { return fetch('/profile').then(r => r.json()); }\n",
    "auth": "export async function getSession() { return fetch('/session').then(r => r.json()); }\n",
    "search": "export async function search(q: string) { return fetch(`/search?q=${q}`).then(r => r.json()); }\n",
    "uploads": "export async function upload(f: File) { return fetch('/uploads', { method: 'POST', body: f }); }\n",
    "notifications": "export async function getNotifications() { return fetch('/notifications').then(r => r.json()); }\n",
    "analytics": "export function track(event: string) { void event; }\n",
}


def simple_component(name: str) -> str:
    return (
        f"type {name}Props = {{ className?: string; children?: React.ReactNode }};\n"
        f"export function {name}({{ className, children }}: {name}Props) {{\n"
        f'  return <div className={{className}} data-component="{name}">{{children}}</div>;\n'
        f"}}\n"
    )


def write(path: str, body: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(body)


def main() -> int:
    root = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), "existing")
    count = 0

    for name, body in UI_PRIMITIVES.items():
        write(os.path.join(root, "src/components/ui", f"{name}.tsx"), body)
        count += 1
    for name in DECOYS + FILLER_UI:
        write(os.path.join(root, "src/components/ui", f"{name}.tsx"), simple_component(name))
        count += 1
    for feature, names in FEATURES.items():
        for name in names:
            write(os.path.join(root, "src/components", feature, f"{name}.tsx"), simple_component(name))
            count += 1
    for name, body in API_MODULES.items():
        write(os.path.join(root, "src/api", f"{name}.ts"), body)

    print(f"generated {count} components and {len(API_MODULES)} api modules under {root}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
