# DefCheck

Checks every element in the mod's XML against RimWorld 1.6's own types, the way
the game's loader does: each element must name a field (or a `[LoadAlias]`) on
the type it lands in. Catches "doesn't correspond to any field in type" errors
before the game sees them. Run it after any def change:

```sh
dotnet run --project Source/DefCheck -- Defs/*.xml Defs/*/*.xml
```

It reads Krafs' reference assemblies, so no game install is needed. It does not
check def *references* (a defName that names nothing) - only fields.
