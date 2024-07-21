# Examples

All services provided by the extension are defined using public interfaces. If
you don't understand the logic behind a certain service or want to modify its
behavior, you can extend existing service or create a new service.

Don't try to squeeze project requirements into existing utilities. Instead,
define the optimized services that do the work in the most efficient way. Class
creation is the base principle of ckanext-collection philosophy, so create
classes, and create a lot of them.

In this section you'll find examples of collections that were created in real
project, and examples that exist only for demonstration. You'll notice that
some examples do the same things, but in a different way. For example, packages
or users will be listed using `data.ModelData` in one example, while another
example will use `data.ApiSearchData`.

There are no ideal generic solutions, and often different approaches will be
interchangeable. Check the example, read the explanation, and choose the flow
that is the most efficient and the most readable for you. You can always build
a multiple versions of the same collection, create a benchmark for it and swap
implementation as project evolves. Collection exposes the data, and how this
data is produced is an implementation detail of the collection that is hiddent
from other parts of the application. It means, you'll be able to change
implementation without breaking any code that uses the collection as long as
you keep the output unchanged.
