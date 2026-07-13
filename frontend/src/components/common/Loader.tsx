export default function Loader({ fullscreen = false }: { fullscreen?: boolean }) {
  if (fullscreen) return <div className="page-loading">Загрузка...</div>;
  return <p className="empty-state">Загрузка...</p>;
}
