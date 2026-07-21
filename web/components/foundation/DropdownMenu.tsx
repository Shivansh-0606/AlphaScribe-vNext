/**
 * Dropdown menu (Family 03) — docs/experience_design/Components/03_Selection_Controls.md.
 * Presents actions (not values — that's Select) from a trigger. Re-exported
 * as generated: already correctly token-bound (bg-popover, focus:bg-accent)
 * and already implements the frozen contract — destructive items via
 * `variant="destructive"` on `DropdownMenuItem`, Esc returns focus to the
 * trigger, first item focused on open (all native Radix DropdownMenu
 * behavior, not reimplemented).
 *
 * Usage: keep destructive actions in their own section (a `DropdownMenuSeparator`
 * before them) and require confirmation for irreversible ones at the call site
 * (this primitive renders the menu; it doesn't own the confirmation flow).
 */
export {
  DropdownMenu,
  DropdownMenuCheckboxItem,
  DropdownMenuContent,
  DropdownMenuGroup,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuPortal,
  DropdownMenuRadioGroup,
  DropdownMenuRadioItem,
  DropdownMenuSeparator,
  DropdownMenuShortcut,
  DropdownMenuSub,
  DropdownMenuSubContent,
  DropdownMenuSubTrigger,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
