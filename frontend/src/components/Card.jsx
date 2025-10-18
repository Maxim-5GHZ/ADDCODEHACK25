function Card({ title, description, image }) {
    return (
        <>
            <div className='bg-[var(--neutral-dark-color)] h-auto w-full max-w-[30rem] md:max-w-[50rem] md:h-[60rem] rounded-[4rem] md:rounded-[8rem] shadow-2xl pt-8 md:pt-16'>
                <div className='flex flex-col h-full'>
                    <h3 className='text-2xl md:text-4xl lg:text-6xl text-center text-[var(--neutral-color)] font-bold px-4 md:px-0'>
                        {title}
                    </h3>
                    <p className='text-lg md:text-2xl lg:text-3xl text-[var(--neutral-secondary-color)] m-6 md:m-12 tracking-wider'>
                        {description}
                    </p>
                    <div className="flex-grow">
                        <img loading="lazy" src={image} alt={title} className="w-full h-48 md:h-full object-cover rounded-b-[4rem] md:rounded-b-[8rem]"/>
                    </div>
                </div>
            </div>
        </>
    )
}

function HorizontalCard({ title, description, image }) {
    return (
        <div className="bg-[var(--neutral-secondary-color)] h-auto md:h-[40vh] min-h-[300px] md:min-h-[400px] w-full max-w-6xl rounded-[4rem] md:rounded-[8rem] shadow-2xl overflow-hidden">
            <div className="flex flex-col md:flex-row h-full">
                <div className="flex flex-col justify-center py-6 md:py-8 px-6 md:px-12 w-full md:w-7/12 order-2 md:order-1">
                    <h3 className="text-xl md:text-3xl lg:text-4xl text-[var(--neutral-dark-color)] font-bold mb-4 md:mb-6 text-center md:text-start">
                        {title}
                    </h3>
                    <p className="text-base md:text-xl lg:text-2xl text-[var(--neutral-dark-color)] leading-tight text-center md:text-start">
                        {description}
                    </p>
                </div>

                <div className="w-full md:w-5/12 order-1 md:order-2">
                    <img 
                        loading="lazy" 
                        src={image} 
                        alt={title} 
                        className="w-full h-48 md:h-full object-cover"
                    />
                </div>
            </div>
        </div>
    );
}

export {Card, HorizontalCard}