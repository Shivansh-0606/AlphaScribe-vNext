"use client";

import { DotsThree } from "@phosphor-icons/react/dist/ssr";
import { useRef } from "react";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/foundation/DropdownMenu";
import { IconButton } from "@/components/foundation/IconButton";
import type { ReportListItem } from "../integration/schemas";
import { REPORT_DELETE_COPY as copy } from "./copy";

/**
 * One row's actions menu (SCR-09, CR-SCOPE-004). A one-item menu (Delete) is
 * the accepted launch shape (brief §3.8). Choosing Delete hands the trigger
 * element up so Cancel can return focus to exactly this row's trigger.
 */
export function ReportActionsMenu({
  report,
  onDelete,
}: {
  report: ReportListItem;
  onDelete: (trigger: HTMLElement | null) => void;
}) {
  const triggerRef = useRef<HTMLButtonElement>(null);
  const deleteChosen = useRef(false);

  return (
    // modal={false}: a modal menu and the confirm Dialog both lock body
    // pointer-events while one closes and the other opens (Radix #1241), which
    // can leave the page unclickable.
    <DropdownMenu modal={false}>
      <DropdownMenuTrigger asChild>
        <IconButton
          ref={triggerRef}
          label={copy.menuTriggerLabel(report)}
          icon={<DotsThree weight="bold" />}
          size="sm"
        />
      </DropdownMenuTrigger>
      <DropdownMenuContent
        align="end"
        onCloseAutoFocus={(event) => {
          // After Delete is chosen, focus belongs to the confirm dialog, not back on this trigger.
          if (deleteChosen.current) {
            event.preventDefault();
            deleteChosen.current = false;
          }
        }}
      >
        <DropdownMenuItem
          variant="destructive"
          onSelect={() => {
            deleteChosen.current = true;
            onDelete(triggerRef.current);
          }}
        >
          {copy.menuDeleteItem}
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
