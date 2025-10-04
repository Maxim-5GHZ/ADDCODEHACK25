function Card({ title, description, image }) {
    return (
        <>
            <div className='bg-[var(--neutral-dark-color)] h-[60rem] w-[50rem] rounded-[8rem] shadow-2xl pt-16'>
                <div className='flex flex-col h-full'>
                    <h3 className='text-4xl lg:text-6xl text-center text-[var(--neutral-color)] font-bold'>
                        {title}
                    </h3>
                    <p className='text-2xl lg:text-3xl text-[var(--neutral-secondary-color)] m-12 tracking-wider'>
                        {description}
                    </p>
                    <div className="flex-grow">
                        <img loading="lazy" src={image} alt={title} className="w-full h-full object-cover rounded-b-[8rem]"/>
                    </div>
                </div>
            </div>
        </>
    )
}

function HorizontalCard({ title, description, image }) {
    return (
        <div className="bg-[var(--neutral-secondary-color)] h-[40vh] min-h-[400px] w-[70vw] max-w-6xl rounded-[8rem] shadow-2xl overflow-hidden">
            <div className="flex h-full">
                <div className="flex flex-col justify-center py-8 px-12 w-7/12">
                    <h3 className="text-3xl lg:text-4xl text-[var(--neutral-dark-color)] font-bold mb-6 text-start">
                        {title}
                    </h3>
                    <p className="text-xl lg:text-2xl text-[var(--neutral-dark-color)] leading-tighter text-start">
                        {description}
                    </p>
                </div>

                <div className="w-5/12">
                    <img 
                        loading="lazy" 
                        src={image} 
                        alt={title} 
                        className="w-full h-full object-cover"
                    />
                </div>
            </div>
        </div>
    );
}

export { Card, HorizontalCard }