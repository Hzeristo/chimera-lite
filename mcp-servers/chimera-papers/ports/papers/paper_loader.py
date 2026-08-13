"""Promote MinerU output to a clean Markdown file and materialize a Paper."""

from __future__ import annotations

import logging
import shutil
from pathlib import Path

from core.schemas import Paper, PaperMetadata
from ports.arxiv.arxiv_fetch import ArxivFetcher

logger = logging.getLogger(__name__)


class PaperLoader:
    """Handle markdown file promotion (Rescue) and Paper materialization."""

    def extract_and_clean(
        self, raw_paper_dir: Path, clean_dir: Path, paper_stem: str
    ) -> Path:
        """
        Search for the true Markdown file within a messy MinerU output folder,
        and copy it cleanly to the final directory.

        Args:
            raw_paper_dir: The root folder MinerU generated for this paper (contains /auto, /images etc).
            clean_dir: Target clean directory for processed markdown files.
            paper_stem: The original name of the paper (without .pdf), used for precise matching.

        Returns:
            Path to the promoted markdown file under clean_dir.
        """
        if not raw_paper_dir.exists() or not raw_paper_dir.is_dir():
            raise FileNotFoundError(f"Raw paper directory not found: {raw_paper_dir}")

        clean_dir.mkdir(parents=True, exist_ok=True)
        final_clean_md = clean_dir / f"{paper_stem}.md"

        md_files = list(raw_paper_dir.rglob("*.md"))
        if not md_files:
            raise FileNotFoundError(
                f"Failed extraction: No markdown files found recursively in {raw_paper_dir}"
            )

        best_match: Path | None = None
        for md in md_files:
            if md.stem == paper_stem:
                best_match = md
                break

        if best_match is None:
            best_match = md_files[0]
            logger.warning(
                "[Papers] Could not find an exact match for '%s.md'. Falling back to '%s'",
                paper_stem,
                best_match.name,
            )

        if final_clean_md.exists():
            # Still promote images: papers converted before figures were copied alongside
            # have a clean markdown whose links dangle, and returning here without the copy
            # would make the defect unrepairable by re-running. The copy skips files that
            # already exist, so this is idempotent.
            logger.info(
                "[Papers] Target markdown already exists in clean vault: %s",
                final_clean_md.name,
            )
            self._copy_images_alongside(best_match, clean_dir)
            return final_clean_md

        try:
            shutil.copy2(best_match, final_clean_md)
            logger.info(
                "[Papers] Extracted: %s -> %s", best_match.name, final_clean_md.name
            )
        except OSError as exc:
            logger.error(
                "[Papers] Failed to extract markdown from %s", raw_paper_dir, exc_info=True
            )
            raise RuntimeError(
                f"IO Error during promotion. source={best_match}, target={final_clean_md}"
            ) from exc

        self._copy_images_alongside(best_match, clean_dir)
        return final_clean_md

    @staticmethod
    def _copy_images_alongside(source_md: Path, clean_dir: Path) -> int:
        """Copy MinerU's `images/` next to the clean markdown so its links resolve.

        MinerU writes figure references as `![](images/<sha256>.jpg)` — RELATIVE to the
        markdown. Promoting only the `.md` therefore produced a file whose every image link
        was dangling from the moment it was written; the images stayed behind in the raw
        output directory. That was survivable while the raw tree was permanent, and became
        data loss the moment anything reclaimed it.

        A single shared `clean_dir/images/` is correct rather than a per-paper subdirectory:
        the relative link is exactly `images/<name>`, and MinerU names files by content hash,
        so two papers sharing an identical figure share one file and never collide. Existing
        files are left alone for the same reason — same name means same bytes.

        Never raises: a missing figure must not fail an otherwise good conversion. Returns
        the number of images copied.
        """
        source_images = source_md.parent / "images"
        if not source_images.is_dir():
            return 0
        target_images = clean_dir / "images"
        copied = 0
        try:
            target_images.mkdir(parents=True, exist_ok=True)
            for image in source_images.iterdir():
                if not image.is_file():
                    continue
                destination = target_images / image.name
                if destination.exists():
                    continue
                shutil.copy2(image, destination)
                copied += 1
        except OSError as exc:
            logger.warning(
                "[Papers] Could not copy images from %s: %s — markdown image links will "
                "not resolve for this paper",
                source_images,
                exc,
            )
            return copied
        if copied:
            logger.info("[Papers] Copied %s image(s) -> %s", copied, target_images)
        return copied

    def load_paper(self, clean_md: Path) -> Paper:
        """
        Read clean markdown and construct a strict Paper model.

        Args:
            clean_md: Clean markdown file path.

        Returns:
            Materialized Paper instance.
        """
        if clean_md.suffix.lower() != ".md":
            raise ValueError(f"Expected a .md file, got: {clean_md}")
        if not clean_md.exists():
            raise FileNotFoundError(f"Clean markdown not found: {clean_md}")

        try:
            raw_text = clean_md.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError) as exc:
            logger.error(
                "[Papers] Failed to read markdown file: %s", clean_md, exc_info=True
            )
            raise RuntimeError(
                f"Failed to read markdown file: {clean_md.name}"
            ) from exc

        paper_id = clean_md.stem
        year: str | None = None
        authors: str | None = None

        if ArxivFetcher._extract_arxiv_core_id(paper_id) is not None:
            logger.info("[Papers] Fetching arXiv metadata for %s...", paper_id)
            fetcher = ArxivFetcher(timeout_seconds=5)
            meta = fetcher.fetch_single_metadata(paper_id)
            if meta:
                year = meta["year"]
                authors = meta["authors"]
            else:
                year = "Unknown"
                authors = "Unknown"

        return Paper(
            id=paper_id,
            type="arxiv_paper",
            title=paper_id,
            content_path=clean_md.resolve(),
            raw_text=raw_text,
            year=year,
            authors=authors,
            metadata=PaperMetadata(extracted_from="MinerU"),
        )

    def load_clean_md(self, md_path: Path) -> Paper:
        """Load one already-clean markdown file as a Paper object."""
        return self.load_paper(md_path)
