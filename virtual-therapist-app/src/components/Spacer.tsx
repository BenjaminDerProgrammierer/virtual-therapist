
export default function Spacer({ height, width }: { height?: number, width?: number }) {
    if(height == undefined) height = 1;
    if(width == undefined)  width = 1;
    return <div style={{height, width}}/>
}