import Loading from '@/components/ui/Loading';

export default function RootLoading() {
  return (
    <div className="flex-1 flex items-center justify-center min-h-[50vh]">
      <Loading size="lg" text="Loading..." />
    </div>
  );
}
