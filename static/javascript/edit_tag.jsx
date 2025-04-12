
const EditTag = ({ tagId }) => {
        const [tagData, setTagData] = React.useState({tagId: 0, label: ''})


    React.useEffect(() => {
        fetch(`http://localhost:8000/tags/get_tag/${tagId}`)
            .then(response => {
                return response.json();
            })
            .then(data => {
                setTagData({tagId: data.tagId, label: data.label, is_deleted: data.is_deleted});
            })
            .catch(error => {
                console.error(error);
            });
    }, [tagId]);

    const handleEdit = (event) => {
        const {name, value} = event.target;
        setTagData({...tagData, [name]: value});
    };

    const handleSubmit = (event) => {
        event.preventDefault();
        fetch(`http://localhost:8000/tags/update_tag/${tagId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(tagData),
        })
            .catch(error => {
                console.error(error);
            });
        window.location.href = `/tags/tags_list`;
    };

    return (
        <div>
            <h1> _('Editing tag') </h1>
            <form onSubmit={handleSubmit} >
                <h2> _('Label:') </h2>
                <input
                    type="text"
                    id="label"
                    name="label"
                    value={tagData.label}
                    onChange={handleEdit}
                    required
                    />
                <div>
                    <button type="submit"> _('Submit') </button>
                </div>
            </form>
        </div>
    );
}

const container = document.getElementById('root');
if (container) {
    try {
        const pathIntoParts = window.location.pathname.split("/");
        const urlTagId = pathIntoParts[pathIntoParts.length -1];
        const root = ReactDOM.createRoot(container);
        root.render(<EditTag tagId={urlTagId} />);
    } catch (error) {
        console.error(error);
    }
}