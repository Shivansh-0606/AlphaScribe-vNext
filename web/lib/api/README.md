# `lib/api` — Integration layer (trust boundary)

The single, typed, validated path to the backend contract (03.3). Client + adapters/mappers + Zod validation + error normalization. **No component, feature UI, or store calls the network directly** (03.3 AD-1). TanStack Query config lives here (03.2).
