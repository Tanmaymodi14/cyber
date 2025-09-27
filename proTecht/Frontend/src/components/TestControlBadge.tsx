import { Badge } from './ui/badge';
import { Tooltip, TooltipContent, TooltipTrigger } from './ui/tooltip';

interface TestControlBadgeProps {
  controlId: string;
}

export function TestControlBadge({ controlId }: TestControlBadgeProps) {
  return (
    <Tooltip>
      <TooltipTrigger asChild>
        <Badge variant="outline" className="cursor-help">
          {controlId}
        </Badge>
      </TooltipTrigger>
      <TooltipContent className="bg-black text-white p-2 rounded">
        <p>This is a test tooltip for {controlId}</p>
      </TooltipContent>
    </Tooltip>
  );
}