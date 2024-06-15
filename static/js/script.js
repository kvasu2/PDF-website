// Script.js
const sortableList =
	document.getElementById("sortable");
let draggedItem = null;

sortableList.addEventListener(
	"dragstart",
	(e) => {
		draggedItem = e.target;
		setTimeout(() => {
			e.target.style.display =
				"none";
		}, 0);
});

sortableList.addEventListener(
	"dragend",
	(e) => {
		setTimeout(() => {
			e.target.style.display = "";
			draggedItem = null;
		}, 0);
});

sortableList.addEventListener(
	"dragover",
	(e) => {
		e.preventDefault();
		const afterElement =
			getDragAfterElement(
				sortableList,
				e.clientY);
		const currentElement =
			document.querySelector(
				".dragging");
		if (afterElement == null) {
			sortableList.appendChild(
				draggedItem
			);} 
		else {
			sortableList.insertBefore(
				draggedItem,
				afterElement
			);}
	});

const getDragAfterElement = (
	container, y
) => {
	const draggableElements = [
		...container.querySelectorAll(
			"li:not(.dragging)"
		),];

	return draggableElements.reduce(
		(closest, child) => {
			const box =
				child.getBoundingClientRect();
			const offset =
				y - box.top - box.height / 2;
			if (
				offset < 0 &&
				offset > closest.offset) {
				return {
					offset: offset,
					element: child,
				};} 
			else {
				return closest;
			}},
		{
			offset: Number.NEGATIVE_INFINITY,
		}
	).element;
};

sortableList.addEventListener("dragend", (e) => {
    const sortedList = [];
    const listItems = sortableList.children;
    for (let i = 0; i < listItems.length; i++) {
        sortedList.push(listItems[i].textContent);
    }
    sendSortedList(sortedList);
});

function sendSortedList(sortedList) {
    fetch("/sorted_list", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify(sortedList),
    })
    .then((response) => response.json())
    .then((data) => {
        console.log("Sorted list sent to server:", data);
    })
    .catch((error) => {
        console.error("Error sending sorted list:", error);
    });
}