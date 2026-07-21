import { axe } from "jest-axe";
import { describe, expect, it } from "vitest";
import { renderWithProviders, screen } from "@/tests/setup/render";
import { Button } from "./Button";
import {
  Drawer,
  DrawerContent,
  DrawerDescription,
  DrawerHeader,
  DrawerTitle,
  DrawerTrigger,
} from "./Drawer";

function DemoDrawer(props: { modal?: boolean }) {
  return (
    <Drawer modal={props.modal}>
      <DrawerTrigger asChild>
        <Button>Open filters</Button>
      </DrawerTrigger>
      <DrawerContent modal={props.modal}>
        <DrawerHeader>
          <DrawerTitle>Filters</DrawerTitle>
          <DrawerDescription>Narrow your results.</DrawerDescription>
        </DrawerHeader>
      </DrawerContent>
    </Drawer>
  );
}

describe("Drawer", () => {
  it("opens on trigger click, labeled by its title", async () => {
    const { user } = renderWithProviders(<DemoDrawer />);
    await user.click(screen.getByRole("button", { name: "Open filters" }));
    expect(await screen.findByRole("dialog", { name: "Filters" })).toBeInTheDocument();
  });

  it("closes on Escape and returns focus to the trigger", async () => {
    const { user } = renderWithProviders(<DemoDrawer />);
    const trigger = screen.getByRole("button", { name: "Open filters" });
    await user.click(trigger);
    await screen.findByRole("dialog");
    await user.keyboard("{Escape}");
    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
    expect(trigger).toHaveFocus();
  });

  it("omits the scrim overlay when modal=false (the non-modal companion case)", async () => {
    const { user } = renderWithProviders(<DemoDrawer modal={false} />);
    await user.click(screen.getByRole("button", { name: "Open filters" }));
    await screen.findByRole("dialog");
    // Content is portaled to document.body, outside the render container —
    // query the document directly rather than the RTL container.
    expect(
      document.querySelector('[data-slot="foundation-drawer-overlay"]'),
    ).not.toBeInTheDocument();
  });

  it("has no detectable accessibility violations when open", async () => {
    const { container, user } = renderWithProviders(<DemoDrawer />);
    await user.click(screen.getByRole("button", { name: "Open filters" }));
    await screen.findByRole("dialog");
    expect(await axe(container)).toHaveNoViolations();
  });
});
