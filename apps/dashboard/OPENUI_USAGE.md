# OpenUI Usage

Theta Desk uses OpenUI by thesys as the dashboard UI layer.

- `ThemeProvider` and `createTheme` define the dark trading-terminal theme.
- `Button` powers the scan, cited.md, and Wheeler controls.
- `Card` and `CardHeader` frame the pipeline, candidate screen, brief panel, and bot console.
- `Table`, `TableHeader`, `TableBody`, `TableRow`, `TableHead`, and `TableCell` render the sortable candidate grid.
- `MiniBarChart` renders the annualized-yield mini chart above the candidate table.
- `Tabs`, `TabsList`, `TabsTrigger`, and `TabsContent` organize the locked brief.
- `TextCallout` renders the free summary.
- `Tag` renders sponsor chips and the `SIM` mock-mode badge.

Package note: the prompt requested `@openuidev/react-core`, but that package name is not published on npm as of this implementation. `package.json` installs it as an npm alias to the current OpenUI core runtime package, `@openuidev/react-lang`, while also installing `@openuidev/react-lang` directly for peer dependency resolution.
