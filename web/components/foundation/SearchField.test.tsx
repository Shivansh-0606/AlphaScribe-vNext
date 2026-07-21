import { axe } from "jest-axe";
import { useState } from "react";
import { describe, expect, it, vi } from "vitest";
import { renderWithProviders, screen, waitFor } from "@/tests/setup/render";
import { SearchField, type SearchFieldSuggestion } from "./SearchField";

const SUGGESTIONS: SearchFieldSuggestion[] = [
  { id: "reliance", label: "Reliance Industries", description: "RELIANCE · NSE" },
  { id: "tcs", label: "Tata Consultancy Services", description: "TCS · NSE" },
];

function ControlledSearchField(props: {
  suggestions?: SearchFieldSuggestion[];
  loading?: boolean;
  onSelect?: (s: SearchFieldSuggestion) => void;
  onSubmit?: (value: string) => void;
}) {
  const [value, setValue] = useState("");
  return (
    <SearchField
      label="Search companies"
      value={value}
      onValueChange={setValue}
      suggestions={props.suggestions ?? SUGGESTIONS}
      loading={props.loading}
      onSelect={props.onSelect ?? vi.fn()}
      onSubmit={props.onSubmit}
    />
  );
}

describe("SearchField", () => {
  it("exposes the combobox pattern with the given accessible name", () => {
    renderWithProviders(<ControlledSearchField />);
    expect(screen.getByRole("combobox", { name: "Search companies" })).toBeInTheDocument();
  });

  it("shows a listbox of suggestions once focused and typed into", async () => {
    const { user } = renderWithProviders(<ControlledSearchField />);
    await user.click(screen.getByRole("combobox"));
    await user.type(screen.getByRole("combobox"), "Rel");
    expect(await screen.findByRole("option", { name: /Reliance Industries/ })).toBeInTheDocument();
  });

  it("calls onSelect with the chosen suggestion", async () => {
    const onSelect = vi.fn();
    const { user } = renderWithProviders(<ControlledSearchField onSelect={onSelect} />);
    await user.click(screen.getByRole("combobox"));
    await user.type(screen.getByRole("combobox"), "Rel");
    await user.click(await screen.findByRole("option", { name: /Reliance Industries/ }));
    expect(onSelect).toHaveBeenCalledWith(SUGGESTIONS[0]);
  });

  it("shows the loading state without an empty-results message", async () => {
    const { user } = renderWithProviders(<ControlledSearchField loading suggestions={[]} />);
    await user.click(screen.getByRole("combobox"));
    await user.type(screen.getByRole("combobox"), "Rel");
    expect(await screen.findByText("Searching…")).toBeInTheDocument();
    expect(screen.queryByText(/No results/)).not.toBeInTheDocument();
  });

  it("shows No Results while preserving the typed query in the field", async () => {
    const { user } = renderWithProviders(<ControlledSearchField suggestions={[]} />);
    const combobox = screen.getByRole("combobox");
    await user.click(combobox);
    await user.type(combobox, "Zzzznotfound");
    expect(await screen.findByText(/No results/)).toBeInTheDocument();
    expect(combobox).toHaveValue("Zzzznotfound");
  });

  it("submits on Enter", async () => {
    const onSubmit = vi.fn();
    const { user } = renderWithProviders(
      <ControlledSearchField suggestions={[]} onSubmit={onSubmit} />,
    );
    const combobox = screen.getByRole("combobox");
    await user.click(combobox);
    await user.type(combobox, "Reliance{Enter}");
    expect(onSubmit).toHaveBeenCalledWith("Reliance");
  });

  it("clears the query via a labeled Clear search control, restoring focus", async () => {
    const { user } = renderWithProviders(<ControlledSearchField />);
    const combobox = screen.getByRole("combobox");
    await user.click(combobox);
    await user.type(combobox, "Rel");
    await user.click(await screen.findByRole("button", { name: "Clear search" }));
    await waitFor(() => expect(combobox).toHaveValue(""));
  });

  it("has no detectable accessibility violations with suggestions open", async () => {
    const { container, user } = renderWithProviders(<ControlledSearchField />);
    await user.click(screen.getByRole("combobox"));
    await user.type(screen.getByRole("combobox"), "Rel");
    await screen.findByRole("option", { name: /Reliance Industries/ });
    expect(await axe(container)).toHaveNoViolations();
  });
});
