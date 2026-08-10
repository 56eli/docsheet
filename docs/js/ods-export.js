// =============================================================================
// docs/js/ods-export.js — Zero-dependency OpenDocument Spreadsheet (.ods) export
// Generates styled .ods archives featuring REVISION1 colored block groupings,
// bold headers, and typed numeric/string cells. Imported by app.js.
// =============================================================================

import {
  columnPresetFor,
  orderKeysForView,
} from "./columns.js?v=d185ba911b42";
import {
  humanizeField,
  VIEWS,
} from "./config.js?v=94f497018c49";

const BLOCK_STYLES = {
  "lectures":            { border: "#059669", bg: "#EAF6F2" },
  "discussion":          { border: "#E11D48", bg: "#FCECEF" },
  "satsang":             { border: "#D97706", bg: "#FDF4E8" },
  "on-the-road":         { border: "#0D9488", bg: "#EBF7F6" },
  "volume-series":       { border: "#6366F1", bg: "#F1F2FE" },
  "office-series":       { border: "#0284C7", bg: "#E7F4FC" },
  "books":               { border: "#7C3AED", bg: "#F4EEFE" },
  "transcription-books": { border: "#C026D3", bg: "#FAF0FC" },
  "media-misc":          { border: "#71717A", bg: "#F3F3F3" },
  "lecture-highlights":  { border: "#EA580C", bg: "#FEEFE8" },
  "fran-grace":          { border: "#BE123C", bg: "#FAECEF" },
  "undecided":           { border: "#E2E8F0", bg: "#FFFFFF" },
};

function escapeXml(str) {
  return String(str ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&apos;");
}

/* --------------------------------------------------------------------------- *
 *  CRC-32 and zero-dependency ZIP archive builder (STORE / uncompressed mode)
 * --------------------------------------------------------------------------- */
const _crc32Table = new Uint32Array(256);
for (let i = 0; i < 256; i++) {
  let c = i;
  for (let j = 0; j < 8; j++) {
    c = (c & 1) ? (0xEDB88320 ^ (c >>> 1)) : (c >>> 1);
  }
  _crc32Table[i] = c >>> 0;
}

function crc32(bytes) {
  let crc = 0xFFFFFFFF;
  for (let i = 0; i < bytes.length; i++) {
    crc = (crc >>> 8) ^ _crc32Table[(crc ^ bytes[i]) & 0xFF];
  }
  return (crc ^ 0xFFFFFFFF) >>> 0;
}

function buildZip(files) {
  const encoder = new TextEncoder();
  const fileEntries = files.map((file) => {
    const nameBytes = encoder.encode(file.name);
    const dataBytes = typeof file.data === "string" ? encoder.encode(file.data) : file.data;
    return {
      name: file.name,
      nameBytes,
      dataBytes,
      crc: crc32(dataBytes),
      size: dataBytes.length,
    };
  });

  let totalLocalSize = 0;
  for (const entry of fileEntries) {
    totalLocalSize += 30 + entry.nameBytes.length + entry.size;
  }

  let totalCdSize = 0;
  for (const entry of fileEntries) {
    totalCdSize += 46 + entry.nameBytes.length;
  }

  const archive = new Uint8Array(totalLocalSize + totalCdSize + 22);
  const view = new DataView(archive.buffer);
  let offset = 0;
  const localOffsets = [];

  // 1. Local File Headers and Data
  for (const entry of fileEntries) {
    localOffsets.push(offset);
    view.setUint32(offset, 0x04034b50, true);
    view.setUint16(offset + 4, 20, true);
    view.setUint16(offset + 6, 0x0800, true); // UTF-8 filename flag
    view.setUint16(offset + 8, 0, true);      // STORE method (0)
    view.setUint16(offset + 10, 0, true);     // Time
    view.setUint16(offset + 12, 0, true);     // Date
    view.setUint32(offset + 14, entry.crc, true);
    view.setUint32(offset + 18, entry.size, true);
    view.setUint32(offset + 22, entry.size, true);
    view.setUint16(offset + 26, entry.nameBytes.length, true);
    view.setUint16(offset + 28, 0, true);     // Extra field len
    archive.set(entry.nameBytes, offset + 30);
    offset += 30 + entry.nameBytes.length;
    archive.set(entry.dataBytes, offset);
    offset += entry.size;
  }

  const cdStart = offset;
  // 2. Central Directory Headers
  for (let i = 0; i < fileEntries.length; i++) {
    const entry = fileEntries[i];
    const locOffset = localOffsets[i];
    view.setUint32(offset, 0x02014b50, true);
    view.setUint16(offset + 4, 20, true);
    view.setUint16(offset + 6, 20, true);
    view.setUint16(offset + 8, 0x0800, true);
    view.setUint16(offset + 10, 0, true);
    view.setUint16(offset + 12, 0, true);
    view.setUint16(offset + 14, 0, true);
    view.setUint32(offset + 16, entry.crc, true);
    view.setUint32(offset + 20, entry.size, true);
    view.setUint32(offset + 24, entry.size, true);
    view.setUint16(offset + 28, entry.nameBytes.length, true);
    view.setUint16(offset + 30, 0, true);
    view.setUint16(offset + 32, 0, true);
    view.setUint16(offset + 34, 0, true);
    view.setUint16(offset + 36, 0, true);
    view.setUint32(offset + 38, 0, true);
    view.setUint32(offset + 42, locOffset, true);
    archive.set(entry.nameBytes, offset + 46);
    offset += 46 + entry.nameBytes.length;
  }

  // 3. End of Central Directory Record
  view.setUint32(offset, 0x06054b50, true);
  view.setUint16(offset + 4, 0, true);
  view.setUint16(offset + 6, 0, true);
  view.setUint16(offset + 8, fileEntries.length, true);
  view.setUint16(offset + 10, fileEntries.length, true);
  view.setUint32(offset + 12, totalCdSize, true);
  view.setUint32(offset + 16, cdStart, true);
  view.setUint16(offset + 20, 0, true);

  return archive;
}

/* --------------------------------------------------------------------------- *
 *  ODS OpenDocument XML generator
 * --------------------------------------------------------------------------- */
function generateManifestXml() {
  return `<?xml version="1.0" encoding="UTF-8"?>
<manifest:manifest xmlns:manifest="urn:oasis:names:tc:opendocument:xmlns:manifest:1.0" manifest:version="1.3">
  <manifest:file-entry manifest:full-path="/" manifest:version="1.3" manifest:media-type="application/vnd.oasis.opendocument.spreadsheet"/>
  <manifest:file-entry manifest:full-path="content.xml" manifest:media-type="text/xml"/>
  <manifest:file-entry manifest:full-path="styles.xml" manifest:media-type="text/xml"/>
</manifest:manifest>`;
}

function generateStylesXml() {
  return `<?xml version="1.0" encoding="UTF-8"?>
<office:document-styles xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0" xmlns:style="urn:oasis:names:tc:opendocument:xmlns:style:1.0" xmlns:table="urn:oasis:names:tc:opendocument:xmlns:table:1.0" xmlns:fo="urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0" office:version="1.3">
  <office:styles>
    <style:style style:name="Default" style:family="table-cell"/>
  </office:styles>
</office:document-styles>`;
}

function generateContentXml(data, viewName, getRowBlockId) {
  const preset = columnPresetFor(viewName);
  const allKeys = new Set([
    ...(preset.priority || []),
    ...(preset.hidden || []),
    ...(data.length ? Object.keys(data[0]) : []),
  ]);
  let keys = orderKeysForView([...allKeys], viewName);
  if (keys.includes("year_month")) {
    keys = keys.filter((key) => key !== "year" && key !== "month");
  }
  if (keys.includes("edition")) {
    keys = keys.filter((key) => key !== "format" && key !== "format_detail");
  }

  // Define automatic styles for column widths, header row, and 12 block groups
  let autoStyles = `    <style:style style:name="co1" style:family="table-column">
      <style:table-column-properties fo:break-before="auto" style:column-width="1.6in"/>
    </style:style>
    <style:style style:name="ce-header" style:family="table-cell">
      <style:table-cell-properties fo:background-color="#1A1A1A" fo:padding="0.08in" fo:border="0.01in solid #282828"/>
      <style:text-properties fo:color="#FFFFFF" fo:font-weight="bold" fo:font-family="Roboto, sans-serif" fo:font-size="11pt"/>
    </style:style>`;

  for (const [blockId, style] of Object.entries(BLOCK_STYLES)) {
    autoStyles += `
    <style:style style:name="ce-block-left-${blockId}" style:family="table-cell">
      <style:table-cell-properties fo:background-color="${style.bg}" fo:border-top="0.01in solid #E2E8F0" fo:border-bottom="0.01in solid #E2E8F0" fo:border-right="0.01in solid #E2E8F0" fo:border-left="0.04in solid ${style.border}"/>
      <style:text-properties fo:color="#1A202C" fo:font-family="Roboto, sans-serif" fo:font-size="10pt"/>
    </style:style>
    <style:style style:name="ce-block-mid-${blockId}" style:family="table-cell">
      <style:table-cell-properties fo:background-color="${style.bg}" fo:border-top="0.01in solid #E2E8F0" fo:border-bottom="0.01in solid #E2E8F0" fo:border-right="0.01in solid #E2E8F0" fo:border-left="0.01in solid #E2E8F0"/>
      <style:text-properties fo:color="#1A202C" fo:font-family="Roboto, sans-serif" fo:font-size="10pt"/>
    </style:style>`;
  }

  // Column definitions
  const columnsXml = keys.map(() => `        <table:table-column table:style-name="co1"/>`).join("\n");

  // Header row
  const headerCells = keys
    .map((k) => `          <table:table-cell table:style-name="ce-header" office:value-type="string" calcext:value-type="string"><text:p>${escapeXml(humanizeField(k))}</text:p></table:table-cell>`)
    .join("\n");
  const headerRowXml = `        <table:table-row>\n${headerCells}\n        </table:table-row>`;

  // Data rows
  const dataRowsXml = data.map((row) => {
    const rawBlockId = getRowBlockId ? getRowBlockId(row) : "undecided";
    const blockId = BLOCK_STYLES[rawBlockId] ? rawBlockId : "undecided";
    const cellsXml = keys.map((key, colIdx) => {
      const styleName = colIdx === 0 ? `ce-block-left-${blockId}` : `ce-block-mid-${blockId}`;
      const value = row[key];
      if (value === null || value === undefined || value === "") {
        return `          <table:table-cell table:style-name="${styleName}"/>`;
      }
      const strVal = String(value).trim();
      if (/^-?\d+(\.\d+)?$/.test(strVal)) {
        return `          <table:table-cell table:style-name="${styleName}" office:value-type="float" office:value="${strVal}" calcext:value-type="float"><text:p>${escapeXml(strVal)}</text:p></table:table-cell>`;
      }
      return `          <table:table-cell table:style-name="${styleName}" office:value-type="string" calcext:value-type="string"><text:p>${escapeXml(strVal)}</text:p></table:table-cell>`;
    }).join("\n");
    return `        <table:table-row>\n${cellsXml}\n        </table:table-row>`;
  }).join("\n");

  return `<?xml version="1.0" encoding="UTF-8"?>
<office:document-content xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0" xmlns:style="urn:oasis:names:tc:opendocument:xmlns:style:1.0" xmlns:table="urn:oasis:names:tc:opendocument:xmlns:table:1.0" xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0" xmlns:fo="urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0" xmlns:calcext="urn:org:documentfoundation:names:experimental:calc:xmlns:calcext:1.0" office:version="1.3">
  <office:automatic-styles>
${autoStyles}
  </office:automatic-styles>
  <office:body>
    <office:spreadsheet>
      <table:table table:name="Sheet1">
${columnsXml}
${headerRowXml}
${dataRowsXml}
      </table:table>
    </office:spreadsheet>
  </office:body>
</office:document-content>`;
}

/**
 * Build an in-memory .ods OpenDocument Spreadsheet ZIP archive Uint8Array.
 * Can be tested in Node or browser without external libraries.
 */
export function createOdsArchive(data, viewName, getRowBlockId) {
  const files = [
    { name: "mimetype", data: "application/vnd.oasis.opendocument.spreadsheet" },
    { name: "META-INF/manifest.xml", data: generateManifestXml() },
    { name: "styles.xml", data: generateStylesXml() },
    { name: "content.xml", data: generateContentXml(data, viewName, getRowBlockId) },
  ];
  return buildZip(files);
}

/**
 * Generate and trigger download of an .ods file for the active view.
 */
export function exportOds(data, viewName, getRowBlockId) {
  if (!Array.isArray(data) || !data.length) return;
  const archive = createOdsArchive(data, viewName, getRowBlockId);
  const blob = new Blob([archive], {
    type: "application/vnd.oasis.opendocument.spreadsheet",
  });
  const href = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = href;
  const viewConfig = VIEWS[viewName] || {};
  const baseName = (viewConfig.exportName || "hawkins-export.csv").replace(/\.[a-z]+$/i, "");
  anchor.download = `${baseName}.ods`;
  document.body.append(anchor);
  anchor.click();
  anchor.remove();
  URL.revokeObjectURL(href);
}
