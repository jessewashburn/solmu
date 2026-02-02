import './MetadataList.css';

interface MetadataItem {
  label: string;
  value: string | number | React.ReactNode;
}

interface MetadataListProps {
  items: MetadataItem[];
}

export default function MetadataList({ items }: MetadataListProps) {
  return (
    <dl className="metadata-list">
      {items.map((item, index) => (
        <div key={index} className="metadata-row">
          <dt className="metadata-label">{item.label}</dt>
          <dd className="metadata-value">{item.value}</dd>
        </div>
      ))}
    </dl>
  );
}
