function DeleteUserImage() {
	let Http = new XMLHttpRequest();
	let url = `${window.location.origin}/main/accounts/delete_user_image/`;
	Http.open('GET', url);
	Http.send(null);
}

let anchor = document.getElementById('delete_image_anchor');
anchor.onclick = DeleteUserImage;
