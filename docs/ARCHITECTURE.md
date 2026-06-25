# Architecture

```text
web editor
  └─ theme.json
      ├─ iOS exporter
      │   ├─ renders required CSS file
      │   ├─ generates placeholder PNG assets
      │   └─ packs .ktheme
      └─ Android resource exporter
          ├─ renders colors.xml
          └─ packs resource zip
```

## Design principle

The app stores one platform-neutral `theme.json` and generates target-specific files from it.

## Why no official sample files are bundled

The repository intentionally avoids bundling official sample theme resources, logos, characters, or guide PDFs. Generated placeholder images are created procedurally by this project.

## Required compatibility identifiers

Some generated files contain target-format identifiers such as the required CSS filename and `-kakaotalk-*` CSS properties. These are used only for compatibility with the user-theme format, not for branding this project as an official product.
