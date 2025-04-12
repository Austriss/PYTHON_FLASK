

function ListTags() {
    const [tags, setTags] = React.useState([]);


    React.useEffect(() => {
        fetch('http://localhost:8000/tags/get_tags')
            .then(response => {
                return response.json();
            })
            .then(data => {
                setTags(data);
            })
            .catch(error => {
                console.error(error);
            });
    }, []);

    const handleEditButton = (tagId) => {
        console.log("editing ", tagId);
        window.location.href = `/tags/edit/${tagId}`;
    };

    const handleDeleteButton = (tagId) => {
        fetch(`http://localhost:8000/tags/delete/${tagId}`, {
            method: 'POST'
        })
        console.log("Deleting ", tagId);
    };

    const handleNewTagButton = () => {
        window.location.href = `/tags/new`;
    };

    return (
        <div>
            <div className={"tags-list-title"}>
            <h1> _('tags list from api') </h1>
            </div>
            <ul className={"tag-table"}>
                {tags.map(tag => (
                    <div className={"each-tag-row"} key={tag.tag_id}>
                        id: {tag.tag_id} _('label:') {tag.label}
                        <button className={"tag-button"} onClick={() => handleEditButton(tag.tag_id)}> _('Edit') </button>
                        <button className={"tag-button"} onClick={() => handleDeleteButton(tag.tag_id)}> _('Delete') </button>
                    </div>
                ))}
            </ul>
            <div className={"new-tag-button"}>
                <button onClick={() => handleNewTagButton()} > _('New tag') </button>
            </div>
        </div>
    );

}

const container = document.getElementById('root');
if (container) {
    try {
        const root = ReactDOM.createRoot(container);
        root.render(<ListTags />);
    } catch (error) {
        console.error(error);
    }
}