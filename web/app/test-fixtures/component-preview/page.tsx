"use client";

// Test fixture, not a product page — renders foundation components with
// every variant so Playwright (tests/e2e/component-fixtures.spec.ts) can
// verify real computed styles, which jsdom-based component tests cannot
// (05.1 AD-1: E2E/browser tests are a distinct level from component tests).
// Not linked from anywhere in the product; exists solely as test infrastructure.
// Client Component because Switch/Checkbox controlled states below need
// inline event handlers, which a Server Component can't pass as props.
import { Star } from "@phosphor-icons/react/dist/ssr";
import { useState } from "react";
import { Avatar } from "@/components/foundation/Avatar";
import { Badge } from "@/components/foundation/Badge";
import { Banner } from "@/components/foundation/Banner";
import { Button } from "@/components/foundation/Button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/foundation/Card";
import { Checkbox } from "@/components/foundation/Checkbox";
import { Chip } from "@/components/foundation/Chip";
import { Container } from "@/components/foundation/Container";
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/foundation/Dialog";
import { Divider } from "@/components/foundation/Divider";
import {
  Drawer,
  DrawerContent,
  DrawerDescription,
  DrawerHeader,
  DrawerTitle,
  DrawerTrigger,
} from "@/components/foundation/Drawer";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/foundation/DropdownMenu";
import { Flex } from "@/components/foundation/Flex";
import { FormField } from "@/components/foundation/FormField";
import { Grid } from "@/components/foundation/Grid";
import { Heading } from "@/components/foundation/Heading";
import { IconButton } from "@/components/foundation/IconButton";
import { Input } from "@/components/foundation/Input";
import { Link } from "@/components/foundation/Link";
import { Loader } from "@/components/foundation/Loader";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/foundation/Popover";
import { Progress } from "@/components/foundation/Progress";
import { RadioGroup, RadioGroupItem } from "@/components/foundation/RadioGroup";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/foundation/Select";
import { SearchField, type SearchFieldSuggestion } from "@/components/foundation/SearchField";
import { Skeleton, SkeletonGroup, SkeletonText } from "@/components/foundation/Skeleton";
import { Spacer } from "@/components/foundation/Spacer";
import { Stack } from "@/components/foundation/Stack";
import { Switch } from "@/components/foundation/Switch";
import {
  Table,
  TableBody,
  TableCaption,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/foundation/Table";
import { Text } from "@/components/foundation/Text";
import { Textarea } from "@/components/foundation/Textarea";
import { Tooltip } from "@/components/foundation/Tooltip";

const SEARCH_SUGGESTIONS: SearchFieldSuggestion[] = [
  { id: "reliance", label: "Reliance Industries", description: "RELIANCE · NSE" },
  { id: "tcs", label: "Tata Consultancy Services", description: "TCS · NSE" },
];

export default function ComponentPreviewFixture() {
  const [filterSelected, setFilterSelected] = useState(false);
  const [sortDirection, setSortDirection] = useState<"ascending" | "descending">("descending");
  const [searchValue, setSearchValue] = useState("");

  return (
    <div className="flex flex-col gap-8 p-8">
      <section className="flex flex-col gap-3" data-testid="section-buttons">
        <Heading level="h2">Buttons</Heading>
        <div className="flex flex-wrap items-center gap-3">
          <Button variant="primary" data-testid="button-primary">
            Primary
          </Button>
          <Button variant="secondary" data-testid="button-secondary">
            Secondary
          </Button>
          <Button variant="quiet" data-testid="button-quiet">
            Quiet
          </Button>
          <Button variant="destructive" data-testid="button-destructive">
            Destructive
          </Button>
          <Button variant="primary" hero data-testid="button-hero">
            Hero
          </Button>
          <Button variant="primary" loading data-testid="button-loading">
            Loading
          </Button>
          <Button variant="primary" disabled data-testid="button-disabled">
            Disabled
          </Button>
        </div>
      </section>

      <section className="flex flex-col gap-3" data-testid="section-icon-buttons">
        <Heading level="h2">Icon buttons</Heading>
        <div className="flex flex-wrap items-center gap-3">
          <IconButton
            label="Quiet"
            icon={<Star />}
            variant="quiet"
            data-testid="icon-button-quiet"
          />
          <IconButton
            label="Secondary"
            icon={<Star />}
            variant="secondary"
            data-testid="icon-button-secondary"
          />
          <IconButton
            label="Primary"
            icon={<Star />}
            variant="primary"
            data-testid="icon-button-primary"
          />
          <IconButton
            label="Destructive"
            icon={<Star />}
            variant="destructive"
            data-testid="icon-button-destructive"
          />
        </div>
      </section>

      <section className="flex flex-col gap-2" data-testid="section-typography">
        <Heading level="h2">Typography</Heading>
        <Heading level="h1">Heading 1</Heading>
        <Heading level="h3">Heading 3</Heading>
        <Text variant="body">Body text</Text>
        <Text variant="label">Micro label</Text>
        <Text variant="figure">$1,234,567.89</Text>
        <Text variant="code">const revenue = 42;</Text>
        <Link href="/">Internal link</Link>
        <Link href="https://sec.gov">External link</Link>
      </section>

      <section className="flex flex-col gap-3" data-testid="section-radio-group">
        <Heading level="h2">Radio group</Heading>
        <RadioGroup label="AI access mode" defaultValue="managed" data-testid="radio-group">
          <RadioGroupItem value="managed" label="Managed" />
          <RadioGroupItem value="byok" label="Bring your own key" />
        </RadioGroup>
      </section>

      <section className="flex max-w-sm flex-col gap-3" data-testid="section-input">
        <Heading level="h2">Input</Heading>
        <Input aria-label="Default" data-testid="input-default" />
        <Input aria-label="Invalid" aria-invalid data-testid="input-invalid" />
        <Input aria-label="Disabled" disabled data-testid="input-disabled" />
        <Input type="password" aria-label="Password" data-testid="input-password" />
        <FormField label="Email" error="Enter a valid email.">
          <Input type="email" data-testid="input-in-formfield" />
        </FormField>
      </section>

      <section className="flex max-w-sm flex-col gap-3" data-testid="section-textarea">
        <Heading level="h2">Textarea</Heading>
        <Textarea
          aria-label="Notes"
          defaultValue="One line of text."
          data-testid="textarea-autogrow"
        />
      </section>

      <section className="flex flex-col gap-3" data-testid="section-checkbox">
        <Heading level="h2">Checkbox</Heading>
        <Checkbox label="Unchecked" data-testid="checkbox-unchecked" />
        <Checkbox label="Checked" checked data-testid="checkbox-checked" />
        <Checkbox
          label="Indeterminate"
          checked="indeterminate"
          data-testid="checkbox-indeterminate"
        />
        <Checkbox label="Disabled" disabled data-testid="checkbox-disabled" />
      </section>

      <section className="flex flex-col gap-3" data-testid="section-switch">
        <Heading level="h2">Switch</Heading>
        <Switch label="On" checked onCheckedChange={() => {}} data-testid="switch-on" />
        <Switch label="Off" checked={false} onCheckedChange={() => {}} data-testid="switch-off" />
        <Switch label="Disabled" disabled data-testid="switch-disabled" />
      </section>

      <section className="flex max-w-sm flex-col gap-3" data-testid="section-select">
        <Heading level="h2">Select</Heading>
        <Select>
          <SelectTrigger aria-label="Reporting period" data-testid="select-trigger">
            <SelectValue placeholder="Select a period" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="annual">Annual</SelectItem>
            <SelectItem value="quarterly">Quarterly</SelectItem>
          </SelectContent>
        </Select>
      </section>

      <section className="flex flex-col gap-3" data-testid="section-dropdown-menu">
        <Heading level="h2">Dropdown menu</Heading>
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button data-testid="dropdown-trigger">Actions</Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent>
            <DropdownMenuItem>Rename</DropdownMenuItem>
            <DropdownMenuSeparator />
            <DropdownMenuItem variant="destructive" data-testid="dropdown-item-destructive">
              Delete
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </section>

      <section className="flex flex-col gap-3" data-testid="section-badge">
        <Heading level="h2">Badge</Heading>
        <div className="flex flex-wrap items-center gap-3">
          <Badge variant="neutral" data-testid="badge-neutral">
            Draft
          </Badge>
          <Badge variant="bullish" data-testid="badge-bullish">
            Bullish
          </Badge>
          <Badge variant="bearish" data-testid="badge-bearish">
            Bearish
          </Badge>
          <Badge variant="warning" data-testid="badge-warning">
            Not comparable
          </Badge>
          <Badge variant="verified" data-testid="badge-verified">
            Verified
          </Badge>
          <Badge variant="count" aria-label="3 unread" data-testid="badge-count">
            3
          </Badge>
        </div>
      </section>

      <section className="flex flex-col gap-3" data-testid="section-chip">
        <Heading level="h2">Chip</Heading>
        <div className="flex flex-wrap items-center gap-3">
          <Chip
            variant="filter"
            selected={filterSelected}
            onClick={() => setFilterSelected((v) => !v)}
            data-testid="chip-filter"
          >
            Technology
          </Chip>
          <Chip variant="choice" data-testid="chip-choice">
            Suggest a follow-up
          </Chip>
          <Chip variant="removable" onRemove={() => {}} data-testid="chip-removable">
            Reliance Industries
          </Chip>
          <Chip variant="static" data-testid="chip-static">
            12 results
          </Chip>
        </div>
      </section>

      <section className="flex flex-col gap-3" data-testid="section-avatar">
        <Heading level="h2">Avatar</Heading>
        <div className="flex items-center gap-3">
          <Avatar name="Priya Sharma" size="sm" data-testid="avatar-sm" />
          <Avatar name="Priya Sharma" size="md" data-testid="avatar-md" />
          <Avatar name="Priya Sharma" size="lg" data-testid="avatar-lg" />
          <Avatar name="Amit Verma" size="md" statusLabel="Online" data-testid="avatar-status" />
        </div>
      </section>

      <section className="flex flex-col gap-3" data-testid="section-card">
        <Heading level="h2">Card</Heading>
        <div className="flex flex-wrap gap-4">
          <Card data-testid="card-static" className="w-64">
            <CardHeader>
              <CardTitle>Static card</CardTitle>
            </CardHeader>
            <CardContent>Flat at rest, no shadow.</CardContent>
          </Card>
          <Card asChild variant="interactive" className="w-64" data-testid="card-interactive">
            <a href="#interactive-card">
              <CardHeader>
                <CardTitle>Interactive card</CardTitle>
              </CardHeader>
              <CardContent>Lifts on hover/focus.</CardContent>
            </a>
          </Card>
          <Card variant="selectable" selected className="w-64" data-testid="card-selectable">
            <CardHeader>
              <CardTitle>Selectable card</CardTitle>
            </CardHeader>
            <CardContent>Selected — ring + border cue.</CardContent>
          </Card>
          <Card
            variant="selectable"
            selected={false}
            className="w-64"
            data-testid="card-selectable-unselected"
          >
            <CardHeader>
              <CardTitle>Unselected option</CardTitle>
            </CardHeader>
            <CardContent>No ring/border cue.</CardContent>
          </Card>
        </div>
      </section>

      <section className="flex flex-col gap-3" data-testid="section-table">
        <Heading level="h2">Table</Heading>
        <Table data-testid="table">
          <TableCaption>Revenue by quarter</TableCaption>
          <TableHeader sticky>
            <TableRow>
              <TableHead>Quarter</TableHead>
              <TableHead
                numeric
                sortDirection={sortDirection}
                onSort={() =>
                  setSortDirection((d) => (d === "ascending" ? "descending" : "ascending"))
                }
                data-testid="table-sort-header"
              >
                Revenue
              </TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            <TableRow>
              <TableCell>Q1</TableCell>
              <TableCell numeric>1,234.56</TableCell>
            </TableRow>
            <TableRow>
              <TableCell>Q2</TableCell>
              <TableCell numeric unavailable data-testid="table-cell-unavailable">
                —
              </TableCell>
            </TableRow>
          </TableBody>
        </Table>
      </section>

      <section className="flex flex-col gap-3" data-testid="section-layout">
        <Heading level="h2">Layout primitives</Heading>
        <Stack gap={2} data-testid="layout-stack">
          <Text variant="body">Stack item 1</Text>
          <Text variant="body">Stack item 2</Text>
        </Stack>
        <Divider />
        <Flex gap={3} align="center" data-testid="layout-flex">
          <Text variant="body">Flex item 1</Text>
          <Text variant="body">Flex item 2</Text>
        </Flex>
        <Grid cols={{ base: 4, md: 8, lg: 12 }} gap={2} data-testid="layout-grid">
          <div className="bg-muted p-2">1</div>
          <div className="bg-muted p-2">2</div>
          <div className="bg-muted p-2">3</div>
        </Grid>
        <Container data-testid="layout-container" className="bg-muted">
          <Text variant="body">Container content</Text>
        </Container>
        <Flex data-testid="layout-spacer-demo">
          <Text variant="body">Left</Text>
          <Spacer axis="horizontal" size={4} />
          <Text variant="body">Right</Text>
        </Flex>
      </section>

      <section className="flex max-w-sm flex-col gap-3" data-testid="section-progress">
        <Heading level="h2">Progress</Heading>
        <Progress label="Export progress" value={40} data-testid="progress-determinate" />
        <Progress label="AI analysis" value={70} tone="brand" data-testid="progress-brand" />
        <Progress label="Loading filings" data-testid="progress-indeterminate" />
      </section>

      <section className="flex flex-col gap-3" data-testid="section-skeleton">
        <Heading level="h2">Skeleton</Heading>
        <SkeletonGroup label="Loading company summary" className="flex max-w-sm flex-col gap-2">
          <Skeleton className="h-6 w-1/2" data-testid="skeleton-shape" />
          <SkeletonText lines={3} />
        </SkeletonGroup>
      </section>

      <section className="flex flex-col gap-3" data-testid="section-loader">
        <Heading level="h2">Loader</Heading>
        <Loader label="Loading region" data-testid="loader-region" />
      </section>

      <section className="flex flex-col gap-3" data-testid="section-banner">
        <Heading level="h2">Banner</Heading>
        <Banner tone="info" data-testid="banner-info">
          You&apos;re viewing cached data.
        </Banner>
        <Banner tone="success" data-testid="banner-success">
          Export completed.
        </Banner>
        <Banner
          tone="warning"
          title="Partial data"
          data-testid="banner-warning"
          onDismiss={() => {}}
        >
          Some figures are unavailable for this period.
        </Banner>
        <Banner tone="error" data-testid="banner-error">
          Failed to load filings.
        </Banner>
      </section>

      <section className="flex flex-col gap-3" data-testid="section-tooltip">
        <Heading level="h2">Tooltip</Heading>
        <Tooltip content="Net income after tax">
          <button type="button" data-testid="tooltip-trigger">
            P/E ratio
          </button>
        </Tooltip>
      </section>

      <section className="flex flex-col gap-3" data-testid="section-popover">
        <Heading level="h2">Popover</Heading>
        <Popover>
          <PopoverTrigger asChild>
            <Button data-testid="popover-trigger">Filters</Button>
          </PopoverTrigger>
          <PopoverContent data-testid="popover-content">Filter options</PopoverContent>
        </Popover>
      </section>

      <section className="flex flex-col gap-3" data-testid="section-dialog">
        <Heading level="h2">Dialog</Heading>
        <Dialog>
          <DialogTrigger asChild>
            <Button data-testid="dialog-trigger">Delete report</Button>
          </DialogTrigger>
          <DialogContent showCloseButton data-testid="dialog-content">
            <DialogHeader>
              <DialogTitle>Delete this report?</DialogTitle>
              <DialogDescription>This cannot be undone.</DialogDescription>
            </DialogHeader>
            <DialogFooter>
              <DialogClose asChild>
                <Button variant="quiet">Cancel</Button>
              </DialogClose>
              <Button variant="destructive">Delete</Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </section>

      <section className="flex flex-col gap-3" data-testid="section-drawer">
        <Heading level="h2">Drawer</Heading>
        <div className="flex flex-wrap gap-3">
          <Drawer>
            <DrawerTrigger asChild>
              <Button data-testid="drawer-trigger">Open filters (modal)</Button>
            </DrawerTrigger>
            <DrawerContent data-testid="drawer-content">
              <DrawerHeader>
                <DrawerTitle>Filters</DrawerTitle>
                <DrawerDescription>Narrow your results.</DrawerDescription>
              </DrawerHeader>
            </DrawerContent>
          </Drawer>
          <Drawer modal={false}>
            <DrawerTrigger asChild>
              <Button data-testid="drawer-companion-trigger">Open companion (non-modal)</Button>
            </DrawerTrigger>
            <DrawerContent modal={false} data-testid="drawer-companion-content">
              <DrawerHeader>
                <DrawerTitle>AI companion</DrawerTitle>
                <DrawerDescription>Summoned alongside your work.</DrawerDescription>
              </DrawerHeader>
            </DrawerContent>
          </Drawer>
        </div>
      </section>

      <section className="flex max-w-sm flex-col gap-3" data-testid="section-search-field">
        <Heading level="h2">SearchField</Heading>
        <SearchField
          label="Search companies"
          placeholder="Search companies…"
          value={searchValue}
          onValueChange={setSearchValue}
          suggestions={
            searchValue.trim()
              ? SEARCH_SUGGESTIONS.filter((s) =>
                  s.label.toLowerCase().includes(searchValue.trim().toLowerCase()),
                )
              : []
          }
          onSelect={() => {}}
        />
      </section>
    </div>
  );
}
