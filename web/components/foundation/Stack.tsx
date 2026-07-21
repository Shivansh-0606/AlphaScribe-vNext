import { Flex, type FlexProps } from "./Flex";

/**
 * Stack — the vertical-rhythm shorthand for `Flex` (`direction="col"`).
 * Composition, not a separate implementation — same gap scale, same props.
 */
export type StackProps = Omit<FlexProps, "direction" | "wrap">;

export function Stack({ gap = 4, ...props }: StackProps) {
  return <Flex direction="col" gap={gap} {...props} />;
}
