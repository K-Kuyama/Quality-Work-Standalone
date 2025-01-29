import {useDroppable} from '@dnd-kit/core';

function DroppableArea(props) {

  const {isOver, setNodeRef} = useDroppable({
    id: props.id,
  });
  
  const style = {
  	borderWidth: "2px",
  	borderStyle: "solid",
  	borderColor: isOver ? '#f0f0f0' : undefined,
  	marginTop: "6px",
  	//  	border: "1px soid #f0f0f0",
//  	borderColor: 'white',
  }
  
  return (
    <div ref={setNodeRef} style={style}>
      {props.children}
    </div>
  );
}

export default DroppableArea;