import asyncio
import base64
import json
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import httpx


class ChunkingTest:
    """Test PDF chunking and Markdown conversion."""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=120.0)

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        await self.client.aclose()

    def print_header(self, title: str):
        """Print header."""
        print("\n" + "=" * 80)
        print(f"  {title}")
        print("=" * 80)

    def print_divider(self):
        """Print divider."""
        print("-" * 80)

    async def extract_with_strategy(
        self, pdf_path: str
    ) -> Tuple[Optional[Dict[str, Any]], float]:
        """Extract PDF with smart chunking strategy."""
        try:
            # Read and encode PDF
            pdf_bytes = Path(pdf_path).read_bytes()
            pdf_base64 = base64.b64encode(pdf_bytes).decode("utf-8")

            # Prepare parameters
            parameters = {
                "file_data": pdf_base64,
            }

            # Execute
            payload = {"tool": "pdf_to_text", "parameters": parameters}

            response = await self.client.post(
                f"{self.base_url}/api/mcp/tools/execute", json=payload
            )

            if response.status_code != 200:
                print(f"❌ Error: {response.status_code}")
                print(response.text)
                return None, 0.0

            data = response.json()

            # Save extraction result
            with open("output_extraction.json", "w") as f:
                json.dump(data, f, indent=2)

            return data["result"], data["execution_time"]

        except Exception as e:
            print(f"❌ Exception: {str(e)}")
            import traceback

            traceback.print_exc()
            return None, 0.0

    async def convert_to_markdown(
        self, content: str, chunk_index: int = 0
    ) -> Tuple[Optional[str], float]:
        """Convert text to Markdown."""
        try:
            payload = {
                "tool": "text_to_markdown",
                "parameters": {
                    "content": content,
                },
            }

            response = await self.client.post(
                f"{self.base_url}/api/mcp/tools/execute", json=payload
            )

            if response.status_code != 200:
                print(
                    f"❌ Error converting chunk {chunk_index}: {response.status_code}"
                )
                print(response.text)
                return None, 0.0

            data = response.json()

            # Your tool returns TextToMarkdownResult with 'markdown' field
            markdown = data["result"]["markdown"]
            exec_time = data.get("execution_time", 0.0)

            return markdown, exec_time

        except Exception as e:
            print(f"❌ Exception converting chunk {chunk_index}: {str(e)}")
            import traceback

            traceback.print_exc()
            return None, 0.0

    async def test_smart_chunking(self, pdf_path: str):
        """Test smart chunking."""
        self.print_header("PDF SMART CHUNKING TEST")

        result, exec_time = await self.extract_with_strategy(pdf_path)

        if not result:
            print("❌ Extraction failed.")
            return None

        print(f"✅ Extraction succeeded in {exec_time:.2f} seconds")
        print(f"📄 Pages: {result['metadata']['page_count']}")
        print(f"📦 Total Chunks: {result['total_chunks']}")

        if "statistics" in result:
            stats = result["statistics"]
            print(f"\n📊 Statistics:")
            print(f"   Total tokens: {stats['total_tokens']:,}")
            print(f"   Avg tokens/chunk: {stats['avg_tokens_per_chunk']:,}")
            print(
                f"   Token range: {stats['token_range']['min']:,} - {stats['token_range']['max']:,}"
            )

        # Save chunks to file
        with open("output_chunks.txt", "w") as f:
            for i, chunk in enumerate(result["chunks"]):
                f.write(f"--- Chunk {i} (Tokens: {chunk['token_count']}) ---\n")
                f.write(chunk["content"] + "\n\n")

        print(f"\n💾 Chunks saved to: output_chunks.txt")

        return result

    async def test_markdown_conversion(self, chunks_result: Dict[str, Any]):
        """Test Markdown conversion on extracted chunks."""
        self.print_header("MARKDOWN CONVERSION TEST")

        if not chunks_result or not chunks_result.get("chunks"):
            print("❌ No chunks to convert")
            return

        chunks = chunks_result["chunks"]
        total_chunks = len(chunks)

        print(f"📦 Converting {total_chunks} chunks to Markdown...")
        print()

        markdown_results = []
        total_conversion_time = 0.0

        for i, chunk in enumerate(chunks):
            self.print_divider()
            print(f"\n🔄 Processing chunk {i + 1}/{total_chunks}")
            print(f"   Pages: {chunk['page_range']}")
            print(f"   Tokens: {chunk['token_count']:,}")
            print(f"   Input length: {len(chunk['content']):,} chars")

            # Convert to markdown
            markdown, exec_time = await self.convert_to_markdown(
                chunk["content"], chunk_index=i
            )

            if markdown:
                total_conversion_time += exec_time
                markdown_results.append(markdown)

                print(f"   ✅ Converted in {exec_time:.2f}s")
                print(f"   Output length: {len(markdown):,} chars")

                # Calculate expansion
                original_len = len(chunk["content"])
                if original_len > 0:
                    expansion = ((len(markdown) / original_len) - 1) * 100
                    print(f"   Expansion: {expansion:+.1f}%")
            else:
                print(f"   ❌ Conversion failed")
                markdown_results.append(None)

        # Summary
        self.print_divider()
        print(f"\n📊 CONVERSION SUMMARY")
        print(f"   Total chunks: {total_chunks}")
        print(f"   Successful: {sum(1 for r in markdown_results if r)}")
        print(f"   Failed: {sum(1 for r in markdown_results if not r)}")
        print(f"   Total time: {total_conversion_time:.2f}s")

        if total_chunks > 0:
            print(f"   Avg time/chunk: {total_conversion_time / total_chunks:.2f}s")

        # Save individual markdown files
        output_dir = Path("output_markdown")
        output_dir.mkdir(exist_ok=True)

        for i, (chunk, markdown) in enumerate(zip(chunks, markdown_results)):
            if markdown:
                filename = output_dir / f"chunk_{i:02d}_pages_{chunk['page_range']}.md"
                with open(filename, "w") as f:
                    f.write(
                        f"<!-- Chunk {i} | Pages: {chunk['page_range']} | Tokens: {chunk['token_count']} -->\n\n"
                    )
                    f.write(markdown)

        # Combine all markdown
        combined_markdown = [md for md in markdown_results if md]

        if combined_markdown:
            combined_file = output_dir / "combined_lecture.md"
            with open(combined_file, "w") as f:
                f.write("\n\n---\n\n".join(combined_markdown))

            print(f"\n💾 Markdown saved to: {output_dir}/")
            print(f"   - Individual chunks: chunk_XX_pages_X-X.md")
            print(f"   - Combined file: combined_lecture.md")

            # Show preview of first chunk
            if combined_markdown[0]:
                preview = combined_markdown[0][:300].replace("\n", " ")
                print(f"\n📝 Preview of first chunk:")
                print(f"   {preview}...")

        return markdown_results

    async def test_full_pipeline(self, pdf_path: str):
        """Test complete pipeline: PDF → Chunks → Markdown."""
        self.print_header("FULL PIPELINE TEST: PDF → CHUNKS → MARKDOWN")

        print(f"\n📄 PDF: {Path(pdf_path).name}")
        print(f"💾 Size: {Path(pdf_path).stat().st_size / 1024:.1f} KB")

        # Step 1: Extract and chunk
        chunks_result = await self.test_smart_chunking(pdf_path)

        if not chunks_result:
            return

        # Step 2: Convert to markdown
        await self.test_markdown_conversion(chunks_result)

        self.print_divider()
        print("\n✅ PIPELINE COMPLETE!")
        print("\nGenerated files:")
        print("   - output_extraction.json (raw extraction data)")
        print("   - output_chunks.txt (plain text chunks)")
        print("   - output_markdown/ (formatted markdown)")


async def main():
    """Run the tests."""
    pdf_path = "/Users/marin/Desktop/deep.pdf"

    # Check if server is running
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "http://localhost:8000/api/mcp/health", timeout=5.0
            )
            if response.status_code != 200:
                print("❌ Server is not responding correctly")
                print("   Make sure to run: uv run uvicorn app.main:app --reload")
                return
    except Exception as e:
        print("❌ Cannot connect to server")
        print(f"   Error: {str(e)}")
        print("   Make sure to run: uv run uvicorn app.main:app --reload")
        return

    # Run full pipeline test
    async with ChunkingTest() as tester:
        await tester.test_full_pipeline(pdf_path)

    print("\n" + "=" * 80)
    print("  ALL TESTS COMPLETE")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
