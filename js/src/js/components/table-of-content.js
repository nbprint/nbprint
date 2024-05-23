export function createToc(config) {
  const content = config.content;
  const tocElement = config.tocElement;
  const titleElements = config.titleElements;

  let tocElementDiv = content.querySelector(tocElement);
  if (tocElementDiv) {
    let tocUl = document.createElement("ul");
    tocUl.id = "list-toc-generated";
    tocElementDiv.appendChild(tocUl);

    // add class to all title elements
    let tocElementNbr = 0;
    for (var i = 0; i < titleElements.length; i++) {
      let titleHierarchy = i + 1;
      let titleElement = content.querySelectorAll(titleElements[i]);

      // filter by position in dom, only include things after the ToC
      titleElement = Array.from(titleElement).filter((elem) => {
        return tocElementDiv.compareDocumentPosition(elem) & 0x04;
      });


      titleElement.forEach((element) => {
        // add classes to the element
        element.classList.add("title-element");
        element.setAttribute("data-title-level", titleHierarchy);

        tocElementNbr++;
        // set ID to avoid dupes
        element.id = "title-element-" + tocElementNbr;

      });
    }

    // create toc list
    let tocElements = content.querySelectorAll(".title-element");

    for (var i = 0; i < tocElements.length; i++) {
      let tocElement = tocElements[i];

      let tocNewLi = document.createElement("li");

      // Add class for the hierarcy of toc
      tocNewLi.classList.add("toc-element");
      tocNewLi.classList.add(
        "toc-element-level-" + tocElement.dataset.titleLevel,
      );

      // Keep class of title elements
      let classTocElement = tocElement.classList;
      for (var n = 0; n < classTocElement.length; n++) {
        if (classTocElement[n] != "title-element") {
          tocNewLi.classList.add(classTocElement[n]);
        }
      }

      // Create the element
      tocNewLi.innerHTML =
        '<a href="#' + tocElement.id + '">' + tocElement.innerHTML + "</a>";
      tocUl.appendChild(tocNewLi);
    }
  }
}
